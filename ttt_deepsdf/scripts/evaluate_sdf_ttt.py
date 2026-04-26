#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def configure_torch_performance():
    if not torch.cuda.is_available():
        return
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    try:
        torch.set_float32_matmul_precision("high")
    except Exception:
        pass


def add_deepsdf_to_path(deepsdf_dir):
    if deepsdf_dir not in sys.path:
        sys.path.insert(0, deepsdf_dir)


def load_specs(experiment_dir):
    specs_path = os.path.join(experiment_dir, "specs.json")
    with open(specs_path, "r", encoding="utf-8") as f:
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
    cleaned = {
        key[7:] if key.startswith("module.") else key: value
        for key, value in state_dict.items()
    }
    decoder.load_state_dict(cleaned)
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


def maybe_limit_items(items, max_items):
    if max_items is None:
        return items
    return items[:max_items]


def parse_layer_list(value):
    if not value:
        return []
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def sample_sdf_tensor(data_obj, deep_sdf_module, num_samples):
    sdf = deep_sdf_module.data.unpack_sdf_samples(data_obj, num_samples)
    if isinstance(sdf, torch.Tensor):
        sdf = sdf.cpu().numpy()
    points = torch.from_numpy(sdf[:, :3]).float()
    sdf_gt = sdf[:, 3].astype(np.float32)
    return points, sdf_gt


def load_sdf_tensors(sdf_path, deep_sdf_module, device):
    with np.load(sdf_path) as npz:
        pos = deep_sdf_module.data.remove_nans(torch.from_numpy(npz["pos"]).float())
        neg = deep_sdf_module.data.remove_nans(torch.from_numpy(npz["neg"]).float())
    return pos.to(device), neg.to(device)


def sample_loaded_sdf_tensors(pos_tensor, neg_tensor, num_samples):
    half = int(num_samples / 2)
    random_pos = torch.randint(
        pos_tensor.shape[0], (half,), device=pos_tensor.device
    )
    random_neg = torch.randint(
        neg_tensor.shape[0], (half,), device=neg_tensor.device
    )
    sample_pos = torch.index_select(pos_tensor, 0, random_pos)
    sample_neg = torch.index_select(neg_tensor, 0, random_neg)
    samples = torch.cat([sample_pos, sample_neg], 0)
    return samples[:, :3], samples[:, 3].float()


class ResidualAdapter(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(4, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
        final = self.net[-1]
        nn.init.zeros_(final.weight)
        nn.init.zeros_(final.bias)

    def forward(self, xyz, base_pred):
        adapter_input = torch.cat([xyz, base_pred], dim=1)
        return self.net(adapter_input)


class LoRALinearAdapter(nn.Module):
    def __init__(self, in_dim, out_dim, rank, alpha, freeze_down=False):
        super().__init__()
        self.down = nn.Linear(in_dim, rank, bias=False)
        self.up = nn.Linear(rank, out_dim, bias=False)
        self.scale = alpha / max(rank, 1)
        nn.init.kaiming_uniform_(self.down.weight, a=np.sqrt(5))
        nn.init.zeros_(self.up.weight)
        if freeze_down:
            self.down.weight.requires_grad_(False)

    def forward(self, inputs):
        return self.up(self.down(inputs)) * self.scale


class DecoderLoRAAdapter(nn.Module):
    def __init__(self, decoder, layer_indices, rank, alpha, freeze_down=False):
        super().__init__()
        self.layer_indices = list(layer_indices)
        self.layers = nn.ModuleDict()
        for layer in self.layer_indices:
            lin = getattr(decoder, "lin" + str(layer))
            self.layers[str(layer)] = LoRALinearAdapter(
                in_dim=lin.in_features,
                out_dim=lin.out_features,
                rank=rank,
                alpha=alpha,
                freeze_down=freeze_down,
            )

    def forward_decoder(self, decoder, decoder_input):
        xyz = decoder_input[:, -3:]

        if decoder_input.shape[1] > 3 and decoder.latent_dropout:
            latent_vecs = F.dropout(
                decoder_input[:, :-3], p=0.2, training=decoder.training
            )
            x = torch.cat([latent_vecs, xyz], dim=1)
        else:
            x = decoder_input

        for layer in range(0, decoder.num_layers - 1):
            if layer in decoder.latent_in:
                x = torch.cat([x, decoder_input], dim=1)
            elif layer != 0 and decoder.xyz_in_all:
                x = torch.cat([x, xyz], dim=1)

            lin = getattr(decoder, "lin" + str(layer))
            base = lin(x)
            layer_key = str(layer)
            if layer_key in self.layers:
                base = base + self.layers[layer_key](x)
            x = base

            if layer == decoder.num_layers - 2 and decoder.use_tanh:
                x = decoder.tanh(x)
            if layer < decoder.num_layers - 2:
                if (
                    decoder.norm_layers is not None
                    and layer in decoder.norm_layers
                    and not decoder.weight_norm
                ):
                    bn = getattr(decoder, "bn" + str(layer))
                    x = bn(x)
                x = decoder.relu(x)
                if decoder.dropout is not None and layer in decoder.dropout:
                    x = F.dropout(x, p=decoder.dropout_prob, training=decoder.training)

        if hasattr(decoder, "th"):
            x = decoder.th(x)

        return x


def module_weight_l2(module):
    params = [param for param in module.parameters() if param.requires_grad]
    if not params:
        return torch.zeros(())
    total = torch.zeros((), device=params[0].device)
    for param in params:
        total = total + param.pow(2).sum()
    return total


def count_trainable_params(params_or_module):
    if isinstance(params_or_module, nn.Module):
        params = params_or_module.parameters()
    else:
        params = params_or_module
    return int(sum(param.numel() for param in params if param.requires_grad))


def make_ttt_module(
    decoder,
    mode,
    hidden_dim,
    lora_rank,
    lora_alpha,
    lora_layers,
):
    if mode == "residual":
        return ResidualAdapter(hidden_dim)
    if mode == "lora":
        return DecoderLoRAAdapter(
            decoder=decoder,
            layer_indices=lora_layers,
            rank=lora_rank,
            alpha=lora_alpha,
            freeze_down=False,
        )
    if mode == "lora-fa":
        return DecoderLoRAAdapter(
            decoder=decoder,
            layer_indices=lora_layers,
            rank=lora_rank,
            alpha=lora_alpha,
            freeze_down=True,
        )
    raise ValueError(f"Unsupported TTT mode: {mode}")


def forward_with_ttt_module(decoder, mode, module, points, latent):
    latent_expanded = latent.expand(points.shape[0], -1)
    decoder_input = torch.cat([latent_expanded, points], dim=1)

    if mode == "residual":
        base_pred = decoder(decoder_input)
        residual = module(points, base_pred)
        pred = base_pred + residual
        return pred.reshape(-1), torch.mean(residual.pow(2))

    with torch.no_grad():
        base_pred = decoder(decoder_input)
    pred = module.forward_decoder(decoder, decoder_input)
    delta = pred - base_pred
    return pred.reshape(-1), torch.mean(delta.pow(2))


def default_output_name_for_mode(mode):
    mapping = {
        "residual": "test_ttt_adapter_sdf_mae.json",
        "lora": "test_ttt_lora_sdf_mae.json",
        "lora-fa": "test_ttt_lora_fa_sdf_mae.json",
    }
    return mapping[mode]


def evaluate_test_ttt(
    decoder,
    latents,
    code_length,
    items,
    data_root,
    deep_sdf_module,
    num_samples,
    adapt_samples,
    iters,
    hidden_dim,
    lr_latent,
    lr_adapter,
    latent_reg,
    adapter_reg,
    residual_reg,
    latent_init,
    mode,
    lora_rank,
    lora_alpha,
    lora_layers,
    device,
    log_every=10,
):
    mean_latent = latents.mean(dim=0).detach()
    results = []

    total_items = len(items)

    for index, (dataset_name, class_name, instance_name) in enumerate(items, start=1):
        item_start = time.perf_counter()
        sdf_path = os.path.join(
            data_root, "SdfSamples", dataset_name, class_name, instance_name + ".npz"
        )
        if not os.path.isfile(sdf_path):
            results.append(
                {
                    "instance": instance_name,
                    "mae": None,
                    "missing": True,
                    "seconds": float(time.perf_counter() - item_start),
                }
            )
            if log_every and (index == 1 or index % log_every == 0 or index == total_items):
                print(
                    f"[{index}/{total_items}] {instance_name} missing sdf sample",
                    flush=True,
                )
            continue

        if latent_init == "mean":
            latent_seed = mean_latent.clone()
        else:
            latent_seed = torch.zeros(code_length, device=device)

        latent = latent_seed.unsqueeze(0).to(device).detach().requires_grad_(True)
        module = make_ttt_module(
            decoder=decoder,
            mode=mode,
            hidden_dim=hidden_dim,
            lora_rank=lora_rank,
            lora_alpha=lora_alpha,
            lora_layers=lora_layers,
        ).to(device)
        trainable_params = [param for param in module.parameters() if param.requires_grad]
        latent_trainable_params = int(latent.numel())
        adapter_trainable_params = count_trainable_params(trainable_params)
        total_trainable_params = latent_trainable_params + adapter_trainable_params
        optimizer = torch.optim.Adam(
            [
                {"params": [latent], "lr": lr_latent},
                {"params": trainable_params, "lr": lr_adapter},
            ]
        )

        pos_tensor, neg_tensor = load_sdf_tensors(sdf_path, deep_sdf_module, device)

        for _ in range(iters):
            points, sdf_target = sample_loaded_sdf_tensors(
                pos_tensor, neg_tensor, adapt_samples
            )

            optimizer.zero_grad(set_to_none=True)
            pred, update_penalty = forward_with_ttt_module(
                decoder=decoder,
                mode=mode,
                module=module,
                points=points,
                latent=latent,
            )

            loss = torch.nn.functional.l1_loss(pred, sdf_target)
            loss = loss + latent_reg * torch.mean(latent.pow(2))
            loss = loss + adapter_reg * module_weight_l2(module)
            loss = loss + residual_reg * update_penalty
            loss.backward()
            optimizer.step()

        eval_points, eval_sdf_gt = sample_loaded_sdf_tensors(
            pos_tensor, neg_tensor, num_samples
        )
        with torch.no_grad():
            pred, _ = forward_with_ttt_module(
                decoder=decoder,
                mode=mode,
                module=module,
                points=eval_points,
                latent=latent,
            )

        mae = float(torch.mean(torch.abs(pred - eval_sdf_gt)).item())
        elapsed = float(time.perf_counter() - item_start)
        results.append(
            {
                "instance": instance_name,
                "mae": mae,
                "missing": False,
                "seconds": elapsed,
                "latent_trainable_params": latent_trainable_params,
                "adapter_trainable_params": adapter_trainable_params,
                "total_trainable_params": total_trainable_params,
            }
        )
        if log_every and (index == 1 or index % log_every == 0 or index == total_items):
            print(
                f"[{index}/{total_items}] {instance_name} mae={mae:.6f} seconds={elapsed:.3f}",
                flush=True,
            )

    return results


def evaluate_test_ttt_adapter(**kwargs):
    return evaluate_test_ttt(mode="residual", lora_rank=4, lora_alpha=8.0, lora_layers=[], **kwargs)


def evaluate_test_ttt_lora(
    decoder,
    latents,
    code_length,
    items,
    data_root,
    deep_sdf_module,
    num_samples,
    adapt_samples,
    iters,
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
    mode="lora",
    log_every=10,
):
    return evaluate_test_ttt(
        decoder=decoder,
        latents=latents,
        code_length=code_length,
        items=items,
        data_root=data_root,
        deep_sdf_module=deep_sdf_module,
        num_samples=num_samples,
        adapt_samples=adapt_samples,
        iters=iters,
        hidden_dim=32,
        lr_latent=lr_latent,
        lr_adapter=lr_adapter,
        latent_reg=latent_reg,
        adapter_reg=adapter_reg,
        residual_reg=residual_reg,
        latent_init=latent_init,
        mode=mode,
        lora_rank=lora_rank,
        lora_alpha=lora_alpha,
        lora_layers=lora_layers,
        device=device,
        log_every=log_every,
    )


def summarize(results, payload):
    valid = [item["mae"] for item in results if item["mae"] is not None]
    valid_seconds = [
        item["seconds"]
        for item in results
        if item.get("mae") is not None and item.get("seconds") is not None
    ]
    payload["num_items"] = len(results)
    payload["num_valid"] = len(valid)
    payload["num_missing"] = len(results) - len(valid)
    payload["avg_mae"] = float(np.mean(valid)) if valid else None
    payload["total_seconds_valid"] = float(np.sum(valid_seconds)) if valid_seconds else None
    payload["avg_seconds_per_valid_shape"] = (
        float(np.mean(valid_seconds)) if valid_seconds else None
    )
    payload["median_seconds_per_valid_shape"] = (
        float(np.median(valid_seconds)) if valid_seconds else None
    )
    param_source = next(
        (item for item in results if item.get("total_trainable_params") is not None),
        None,
    )
    if param_source:
        payload["trainable_params"] = {
            "latent": param_source["latent_trainable_params"],
            "adapter": param_source["adapter_trainable_params"],
            "total": param_source["total_trainable_params"],
        }
    payload["results"] = results
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deepsdf-dir", required=True)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--checkpoint", default="latest")
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--split-file")
    parser.add_argument("--max-items", type=int)
    parser.add_argument("--samples", type=int, default=4096)
    parser.add_argument("--adapt-samples", type=int, default=4096)
    parser.add_argument("--iters", type=int, default=200)
    parser.add_argument("--mode", choices=["residual", "lora", "lora-fa"], default="residual")
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
    parser.add_argument("--output-subdir", default="EvaluationTTT")
    parser.add_argument("--output-name")
    parser.add_argument("--log-every", type=int, default=10)
    args = parser.parse_args()

    if args.split_file is not None:
        args.split_file = args.split_file.strip()
    args.mode = args.mode.strip()
    args.output_subdir = args.output_subdir.strip()
    args.output_name = (
        args.output_name.strip()
        if args.output_name is not None
        else default_output_name_for_mode(args.mode)
    )
    lora_layers = parse_layer_list(args.lora_layers)
    if args.mode != "residual" and not lora_layers:
        raise ValueError("LoRA-based modes require at least one target layer")

    add_deepsdf_to_path(args.deepsdf_dir)
    import deep_sdf

    configure_torch_performance()
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    run_start = time.perf_counter()

    specs = load_specs(args.experiment)
    checkpoint_path = os.path.join(
        args.experiment, "ModelParameters", f"{args.checkpoint}.pth"
    )
    latent_path = os.path.join(args.experiment, "LatentCodes", f"{args.checkpoint}.pth")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    decoder = load_decoder(specs, checkpoint_path, device)
    latents = load_training_latents(latent_path, device)
    split_path = args.split_file or specs["TestSplit"]
    items = maybe_limit_items(load_split(split_path), args.max_items)

    results = evaluate_test_ttt(
        decoder=decoder,
        latents=latents,
        code_length=specs["CodeLength"],
        items=items,
        data_root=args.data_root,
        deep_sdf_module=deep_sdf,
        num_samples=args.samples,
        adapt_samples=args.adapt_samples,
        iters=args.iters,
        hidden_dim=args.hidden_dim,
        lr_latent=args.lr_latent,
        lr_adapter=args.lr_adapter,
        latent_reg=args.latent_reg,
        adapter_reg=args.adapter_reg,
        residual_reg=args.residual_reg,
        latent_init=args.latent_init,
        mode=args.mode,
        lora_rank=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_layers=lora_layers,
        device=device,
        log_every=args.log_every,
    )

    output_dir = os.path.join(args.experiment, args.output_subdir, args.checkpoint)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, args.output_name)

    payload = summarize(
        results,
        {
            "mode": args.mode,
            "checkpoint": args.checkpoint,
            "experiment": args.experiment,
            "split_file": split_path,
            "max_items": args.max_items,
            "samples": args.samples,
            "adapt_samples": args.adapt_samples,
            "iters": args.iters,
            "hidden_dim": args.hidden_dim,
            "lora_rank": args.lora_rank,
            "lora_alpha": args.lora_alpha,
            "lora_layers": lora_layers,
            "lr_latent": args.lr_latent,
            "lr_adapter": args.lr_adapter,
            "latent_reg": args.latent_reg,
            "adapter_reg": args.adapter_reg,
            "residual_reg": args.residual_reg,
            "latent_init": args.latent_init,
        },
    )
    payload["wall_seconds"] = float(time.perf_counter() - run_start)
    if torch.cuda.is_available():
        payload["cuda_peak_memory_mb"] = float(
            torch.cuda.max_memory_allocated() / (1024 * 1024)
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(output_path)
    print(f"avg_mae={payload['avg_mae']}")
    print(f"num_valid={payload['num_valid']}")


if __name__ == "__main__":
    main()

