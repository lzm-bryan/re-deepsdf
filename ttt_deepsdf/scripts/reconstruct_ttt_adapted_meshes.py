#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from statistics import mean, median

import numpy as np
import torch
import torch.nn as nn

from evaluate_sdf_ttt import (
    add_deepsdf_to_path,
    configure_torch_performance,
    forward_with_ttt_module,
    load_decoder,
    load_specs,
    load_split,
    load_sdf_tensors,
    load_training_latents,
    make_ttt_module,
    module_weight_l2,
    parse_layer_list,
    sample_loaded_sdf_tensors,
)


class TTTDecoderWrapper(nn.Module):
    def __init__(self, decoder, mode, module):
        super().__init__()
        self.decoder = decoder
        self.mode = mode
        self.module = module

    def forward(self, decoder_input):
        points = decoder_input[:, -3:]
        if self.mode == "baseline":
            return self.decoder(decoder_input)
        if self.mode == "residual":
            base_pred = self.decoder(decoder_input)
            return base_pred + self.module(points, base_pred)
        return self.module.forward_decoder(self.decoder, decoder_input)


def load_split_payload(split_path):
    with open(split_path, "r", encoding="utf-8") as f:
        return json.load(f)


def maybe_limit_items(items, max_items):
    if max_items is None:
        return items
    return items[: max_items]


def find_surface_root(data_root, explicit_surface_root):
    candidates = []
    if explicit_surface_root:
        candidates.append(Path(explicit_surface_root))
    candidates.append(Path(data_root))
    for root in candidates:
        if (root / "SurfaceSamples").is_dir():
            return root
    return None


def optimize_shape(
    decoder,
    latents,
    code_length,
    sdf_path,
    deep_sdf_module,
    adapt_samples,
    eval_samples,
    iters,
    mode,
    hidden_dim,
    lr_latent,
    lr_adapter,
    latent_reg,
    adapter_reg,
    residual_reg,
    latent_init,
    lora_rank,
    lora_alpha,
    lora_layers,
    device,
):
    mean_latent = latents.mean(dim=0).detach()
    latent_seed = mean_latent.clone() if latent_init == "mean" else torch.zeros(code_length, device=device)
    latent = latent_seed.unsqueeze(0).to(device).detach().requires_grad_(True)

    if mode == "baseline":
        module = nn.Identity().to(device)
        trainable_params = []
    else:
        module = make_ttt_module(
            decoder=decoder,
            mode=mode,
            hidden_dim=hidden_dim,
            lora_rank=lora_rank,
            lora_alpha=lora_alpha,
            lora_layers=lora_layers,
        ).to(device)
        trainable_params = [param for param in module.parameters() if param.requires_grad]

    optimizer_groups = [{"params": [latent], "lr": lr_latent}]
    if trainable_params:
        optimizer_groups.append({"params": trainable_params, "lr": lr_adapter})
    optimizer = torch.optim.Adam(optimizer_groups)

    pos_tensor, neg_tensor = load_sdf_tensors(sdf_path, deep_sdf_module, device)
    for _ in range(iters):
        points, sdf_target = sample_loaded_sdf_tensors(pos_tensor, neg_tensor, adapt_samples)
        optimizer.zero_grad(set_to_none=True)
        if mode == "baseline":
            latent_expanded = latent.expand(points.shape[0], -1)
            pred = decoder(torch.cat([latent_expanded, points], dim=1)).reshape(-1)
            update_penalty = torch.zeros((), device=device)
        else:
            pred, update_penalty = forward_with_ttt_module(decoder, mode, module, points, latent)
        loss = torch.nn.functional.l1_loss(pred, sdf_target)
        loss = loss + latent_reg * torch.mean(latent.pow(2))
        if trainable_params:
            loss = loss + adapter_reg * module_weight_l2(module)
            loss = loss + residual_reg * update_penalty
        loss.backward()
        optimizer.step()

    eval_points, eval_sdf_gt = sample_loaded_sdf_tensors(pos_tensor, neg_tensor, eval_samples)
    with torch.no_grad():
        if mode == "baseline":
            latent_expanded = latent.expand(eval_points.shape[0], -1)
            pred = decoder(torch.cat([latent_expanded, eval_points], dim=1)).reshape(-1)
        else:
            pred, _ = forward_with_ttt_module(decoder, mode, module, eval_points, latent)
    mae = float(torch.mean(torch.abs(pred - eval_sdf_gt)).item())
    return latent.detach(), module, mae


def compute_chamfer_for_rows(deep_sdf_module, experiment, checkpoint_label, data_root, surface_root, items):
    import trimesh

    rows = []
    for dataset_name, class_name, instance_name in items:
        mesh_path = (
            Path(experiment)
            / "Reconstructions"
            / checkpoint_label
            / "Meshes"
            / dataset_name
            / class_name
            / f"{instance_name}.ply"
        )
        gt_path = Path(surface_root) / "SurfaceSamples" / dataset_name / class_name / f"{instance_name}.ply"
        norm_path = Path(data_root) / "NormalizationParameters" / dataset_name / class_name / f"{instance_name}.npz"
        if not mesh_path.is_file() or not gt_path.is_file() or not norm_path.is_file():
            rows.append(
                {
                    "shape": f"{dataset_name}/{class_name}/{instance_name}",
                    "chamfer_dist": None,
                    "missing": True,
                }
            )
            continue
        gt = trimesh.load(str(gt_path))
        recon = trimesh.load(str(mesh_path))
        norm = np.load(str(norm_path))
        chamfer = deep_sdf_module.metrics.chamfer.compute_trimesh_chamfer(
            gt, recon, norm["offset"], norm["scale"]
        )
        rows.append(
            {
                "shape": f"{dataset_name}/{class_name}/{instance_name}",
                "chamfer_dist": float(chamfer),
                "missing": False,
            }
        )
    return rows


def write_chamfer_outputs(experiment, label, rows, metadata):
    eval_dir = Path(experiment) / "Evaluation" / label
    eval_dir.mkdir(parents=True, exist_ok=True)
    csv_path = eval_dir / "chamfer.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["shape", "chamfer_dist", "missing"])
        writer.writeheader()
        writer.writerows(rows)

    values = [r["chamfer_dist"] for r in rows if r["chamfer_dist"] is not None]
    summary = {
        **metadata,
        "chamfer_csv": str(csv_path),
        "count": len(values),
        "mean_chamfer": mean(values) if values else None,
        "median_chamfer": median(values) if values else None,
        "min_chamfer": min(values) if values else None,
        "max_chamfer": max(values) if values else None,
        "rows": rows,
    }
    json_path = eval_dir / "summary.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return csv_path, json_path, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deepsdf-dir", required=True)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--split-file", required=True)
    parser.add_argument("--surface-root")
    parser.add_argument("--mode", choices=["baseline", "residual", "lora", "lora-fa"], default="lora")
    parser.add_argument("--output-label", required=True)
    parser.add_argument("--max-items", type=int)
    parser.add_argument("--samples", type=int, default=4096)
    parser.add_argument("--adapt-samples", type=int, default=4096)
    parser.add_argument("--iters", type=int, default=100)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--lora-alpha", type=float, default=16.0)
    parser.add_argument("--lora-layers", default="0,1,2,3,4,5,6,7")
    parser.add_argument("--lr-latent", type=float, default=1e-2)
    parser.add_argument("--lr-adapter", type=float, default=1e-3)
    parser.add_argument("--latent-reg", type=float, default=1e-4)
    parser.add_argument("--adapter-reg", type=float, default=1e-6)
    parser.add_argument("--residual-reg", type=float, default=1e-4)
    parser.add_argument("--latent-init", choices=["mean", "zero"], default="mean")
    parser.add_argument("--resolution", type=int, default=128)
    parser.add_argument("--max-batch", type=int, default=262144)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    add_deepsdf_to_path(args.deepsdf_dir)
    import deep_sdf
    try:
        import skimage.measure as _sk_measure
        if not hasattr(_sk_measure, "marching_cubes_lewiner"):
            _sk_measure.marching_cubes_lewiner = _sk_measure.marching_cubes
    except Exception:
        pass
    configure_torch_performance()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    specs = load_specs(args.experiment)
    checkpoint_path = os.path.join(args.experiment, "ModelParameters", f"{args.checkpoint}.pth")
    latent_path = os.path.join(args.experiment, "LatentCodes", f"{args.checkpoint}.pth")
    decoder = load_decoder(specs, checkpoint_path, device)
    latents = load_training_latents(latent_path, device)
    lora_layers = parse_layer_list(args.lora_layers)
    items = maybe_limit_items(load_split(args.split_file), args.max_items)
    surface_root = find_surface_root(args.data_root, args.surface_root)

    if surface_root is None:
        raise SystemExit("Could not find a SurfaceSamples root")

    mesh_root = Path(args.experiment) / "Reconstructions" / args.output_label / "Meshes"
    state_root = Path(args.experiment) / "Reconstructions" / args.output_label / "TTTStates"
    mesh_root.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)

    run_start = time.perf_counter()
    result_rows = []
    for idx, (dataset_name, class_name, instance_name) in enumerate(items, start=1):
        item_start = time.perf_counter()
        sdf_path = (
            Path(args.data_root)
            / "SdfSamples"
            / dataset_name
            / class_name
            / f"{instance_name}.npz"
        )
        mesh_stem = mesh_root / dataset_name / class_name / instance_name
        state_path = state_root / dataset_name / class_name / f"{instance_name}.pth"
        mesh_stem.parent.mkdir(parents=True, exist_ok=True)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        if args.skip_existing and Path(str(mesh_stem) + ".ply").is_file() and state_path.is_file():
            print(f"[{idx}/{len(items)}] skip existing {instance_name}", flush=True)
            continue
        if not sdf_path.is_file():
            result_rows.append({"instance": instance_name, "mae": None, "missing": True})
            print(f"[{idx}/{len(items)}] missing sdf {instance_name}", flush=True)
            continue

        latent, module, mae = optimize_shape(
            decoder=decoder,
            latents=latents,
            code_length=specs["CodeLength"],
            sdf_path=str(sdf_path),
            deep_sdf_module=deep_sdf,
            adapt_samples=args.adapt_samples,
            eval_samples=args.samples,
            iters=args.iters,
            mode=args.mode,
            hidden_dim=args.hidden_dim,
            lr_latent=args.lr_latent,
            lr_adapter=args.lr_adapter,
            latent_reg=args.latent_reg,
            adapter_reg=args.adapter_reg,
            residual_reg=args.residual_reg,
            latent_init=args.latent_init,
            lora_rank=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_layers=lora_layers,
            device=device,
        )
        wrapper = TTTDecoderWrapper(decoder, args.mode, module).to(device)
        wrapper.eval()
        mesh_error = None
        candidate_batches = []
        for mesh_max_batch in (max(args.max_batch, 131072), 65536, args.max_batch, 32768):
            if mesh_max_batch > 0 and mesh_max_batch not in candidate_batches:
                candidate_batches.append(mesh_max_batch)
        for mesh_max_batch in candidate_batches:
            try:
                with torch.no_grad():
                    deep_sdf.mesh.create_mesh(
                        wrapper,
                        latent,
                        str(mesh_stem),
                        N=args.resolution,
                        max_batch=mesh_max_batch,
                    )
                mesh_error = None
                break
            except RuntimeError as exc:
                mesh_error = str(exc)
                if "out of memory" in mesh_error.lower() and torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    print(
                        f"[{idx}/{len(items)}] retry mesh {instance_name} after OOM with smaller max_batch",
                        flush=True,
                    )
                    continue
                break
            except Exception as exc:
                mesh_error = str(exc)
                break
        torch.save(
            {
                "mode": args.mode,
                "checkpoint": args.checkpoint,
                "instance": instance_name,
                "dataset": dataset_name,
                "class": class_name,
                "latent": latent.detach().cpu(),
                "module_state_dict": module.state_dict() if hasattr(module, "state_dict") else {},
                "mae": mae,
            },
            state_path,
        )
        elapsed = float(time.perf_counter() - item_start)
        result_rows.append(
            {
                "instance": instance_name,
                "mae": mae,
                "missing": False,
                "seconds": elapsed,
                "mesh": str(mesh_stem) + ".ply",
                "state": str(state_path),
                "mesh_error": mesh_error,
            }
        )
        if mesh_error:
            print(
                f"[{idx}/{len(items)}] {instance_name} mae={mae:.6f} mesh_error={mesh_error}",
                flush=True,
            )
        else:
            print(f"[{idx}/{len(items)}] {instance_name} mae={mae:.6f} seconds={elapsed:.2f}", flush=True)

    chamfer_rows = compute_chamfer_for_rows(
        deep_sdf_module=deep_sdf,
        experiment=args.experiment,
        checkpoint_label=args.output_label,
        data_root=args.data_root,
        surface_root=str(surface_root),
        items=items,
    )
    csv_path, json_path, summary = write_chamfer_outputs(
        args.experiment,
        args.output_label,
        chamfer_rows,
        {
            "mode": args.mode,
            "checkpoint": args.checkpoint,
            "output_label": args.output_label,
            "split_file": args.split_file,
            "surface_root": str(surface_root),
            "resolution": args.resolution,
            "iters": args.iters,
            "samples": args.samples,
            "adapt_samples": args.adapt_samples,
            "wall_seconds": float(time.perf_counter() - run_start),
            "shape_results": result_rows,
        },
    )
    print(csv_path)
    print(json_path)
    print(f"mean_chamfer={summary['mean_chamfer']}")
    print(f"median_chamfer={summary['median_chamfer']}")


if __name__ == "__main__":
    main()




