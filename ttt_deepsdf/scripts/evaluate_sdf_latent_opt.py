#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time

import numpy as np
import torch


def add_deepsdf_to_path(deepsdf_dir):
    if deepsdf_dir not in sys.path:
        sys.path.insert(0, deepsdf_dir)


def load_specs(experiment_dir):
    with open(os.path.join(experiment_dir, "specs.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_decoder(specs, checkpoint_path, device):
    arch = __import__("networks." + specs["NetworkArch"], fromlist=["Decoder"])
    decoder = arch.Decoder(
        latent_size=specs["CodeLength"],
        dims=specs["NetworkSpecs"]["dims"],
        dropout=specs["NetworkSpecs"].get("dropout"),
        dropout_prob=specs["NetworkSpecs"].get("dropout_prob", 0.0),
        norm_layers=specs["NetworkSpecs"].get("norm_layers", []),
        latent_in=specs["NetworkSpecs"].get("latent_in", []),
        weight_norm=specs["NetworkSpecs"].get("weight_norm", False),
        xyz_in_all=specs["NetworkSpecs"].get("xyz_in_all", False),
        use_tanh=specs["NetworkSpecs"].get("use_tanh", False),
        latent_dropout=specs["NetworkSpecs"].get("latent_dropout", False),
    )
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = checkpoint["model_state_dict"]
    state_dict = {
        key[7:] if key.startswith("module.") else key: value
        for key, value in state_dict.items()
    }
    decoder.load_state_dict(state_dict)
    decoder = decoder.to(device)
    decoder.eval()
    for param in decoder.parameters():
        param.requires_grad_(False)
    return decoder


def load_training_latents(latent_path, device):
    payload = torch.load(latent_path, map_location=device)
    latents = payload["latent_codes"]
    if isinstance(latents, dict) and "weight" in latents:
        return latents["weight"].to(device)
    return latents.to(device)


def load_split(split_path):
    with open(split_path, "r", encoding="utf-8") as f:
        split = json.load(f)
    items = []
    for dataset_name, class_map in split.items():
        for class_name, instance_list in class_map.items():
            for instance_name in instance_list:
                items.append((dataset_name, class_name, instance_name))
    return items


def load_sdf_tensors(sdf_path, device):
    with np.load(sdf_path) as npz:
        pos = torch.from_numpy(npz["pos"]).float()
        neg = torch.from_numpy(npz["neg"]).float()
    pos = pos[~torch.isnan(pos[:, 3])].to(device)
    neg = neg[~torch.isnan(neg[:, 3])].to(device)
    return pos, neg


def sample_loaded(pos_tensor, neg_tensor, num_samples):
    half = int(num_samples / 2)
    pos_idx = torch.randint(pos_tensor.shape[0], (half,), device=pos_tensor.device)
    neg_idx = torch.randint(neg_tensor.shape[0], (half,), device=neg_tensor.device)
    samples = torch.cat(
        [torch.index_select(pos_tensor, 0, pos_idx), torch.index_select(neg_tensor, 0, neg_idx)],
        dim=0,
    )
    return samples[:, :3], samples[:, 3].float()


def predict(decoder, latent, points):
    latent_expanded = latent.expand(points.shape[0], -1)
    decoder_input = torch.cat([latent_expanded, points], dim=1)
    return decoder(decoder_input).reshape(-1)


def evaluate(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    add_deepsdf_to_path(args.deepsdf_dir)
    specs = load_specs(args.experiment)
    decoder = load_decoder(
        specs,
        os.path.join(args.experiment, "ModelParameters", f"{args.checkpoint}.pth"),
        device,
    )
    latents = load_training_latents(
        os.path.join(args.experiment, "LatentCodes", f"{args.checkpoint}.pth"),
        device,
    )
    mean_latent = latents.mean(dim=0).detach()
    split_path = args.split_file or specs["TestSplit"]
    items = load_split(split_path)
    if args.max_items and args.max_items > 0:
        items = items[: args.max_items]

    results = []
    start_all = time.perf_counter()
    for idx, (dataset_name, class_name, instance_name) in enumerate(items, start=1):
        item_start = time.perf_counter()
        sdf_path = os.path.join(
            args.data_root, "SdfSamples", dataset_name, class_name, instance_name + ".npz"
        )
        if not os.path.isfile(sdf_path):
            results.append(
                {
                    "instance": instance_name,
                    "missing": True,
                    "mae": None,
                    "seconds": time.perf_counter() - item_start,
                }
            )
            continue

        pos, neg = load_sdf_tensors(sdf_path, device)
        if args.latent_init == "mean":
            latent_seed = mean_latent.clone()
        else:
            latent_seed = torch.zeros(specs["CodeLength"], device=device)
        latent = latent_seed.unsqueeze(0).detach().requires_grad_(True)
        optimizer = torch.optim.Adam([latent], lr=args.lr_latent)

        for _ in range(args.iters):
            points, target = sample_loaded(pos, neg, args.adapt_samples)
            optimizer.zero_grad(set_to_none=True)
            pred = predict(decoder, latent, points)
            loss = torch.nn.functional.l1_loss(pred, target)
            loss = loss + args.latent_reg * torch.mean(latent.pow(2))
            loss.backward()
            optimizer.step()

        eval_points, eval_target = sample_loaded(pos, neg, args.samples)
        with torch.no_grad():
            mae = torch.mean(torch.abs(predict(decoder, latent, eval_points) - eval_target)).item()
        results.append(
            {
                "instance": instance_name,
                "missing": False,
                "mae": float(mae),
                "seconds": float(time.perf_counter() - item_start),
            }
        )
        if args.log_every and (idx == 1 or idx % args.log_every == 0 or idx == len(items)):
            print(f"[{idx}/{len(items)}] {instance_name} mae={mae:.6f}", flush=True)

    maes = [row["mae"] for row in results if row.get("mae") is not None]
    summary = {
        "experiment": args.experiment,
        "checkpoint": args.checkpoint,
        "split_file": split_path,
        "data_root": args.data_root,
        "code_length": specs["CodeLength"],
        "iters": args.iters,
        "samples": args.samples,
        "adapt_samples": args.adapt_samples,
        "max_items": args.max_items,
        "num_items": len(items),
        "valid_items": len(maes),
        "missing_items": len(items) - len(maes),
        "mean_mae": float(np.mean(maes)) if maes else None,
        "median_mae": float(np.median(maes)) if maes else None,
        "seconds": float(time.perf_counter() - start_all),
        "per_instance": results,
    }
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(args.output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deepsdf-dir", required=True)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--checkpoint", default="100")
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--split-file")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-items", type=int, default=128)
    parser.add_argument("--samples", type=int, default=8192)
    parser.add_argument("--adapt-samples", type=int, default=8192)
    parser.add_argument("--iters", type=int, default=100)
    parser.add_argument("--lr-latent", type=float, default=1e-2)
    parser.add_argument("--latent-reg", type=float, default=1e-4)
    parser.add_argument("--latent-init", choices=["mean", "zero"], default="mean")
    parser.add_argument("--log-every", type=int, default=25)
    evaluate(parser.parse_args())


if __name__ == "__main__":
    main()


