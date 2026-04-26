#!/usr/bin/env python
"""Create lightweight input manifests for external baseline deployment.

The script does not copy large data. It records official split instances and
candidate surface/input paths so ConvONet/NKSR/POCO conversion scripts can be
written against a stable CSV/JSON contract.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


CLASSES = {
    "airplane": {
        "synset": "02691156",
        "split": "sv2_planes_test.json",
        "surface_root": "external_artifacts/surface_data/airplane",
    },
    "chair": {
        "synset": "03001627",
        "split": "sv2_chairs_test.json",
        "surface_root": "external_artifacts/surface_data/chair",
    },
    "lamp": {
        "synset": "03636649",
        "split": "sv2_lamps_test.json",
        "surface_root": "external_artifacts/surface_data/lamp",
    },
}


def flatten_split(obj: Any) -> list[str]:
    if isinstance(obj, list):
        return [str(x) for x in obj]
    out: list[str] = []
    if isinstance(obj, dict):
        for value in obj.values():
            out.extend(flatten_split(value))
    return out


def candidate_paths(surface_root: str, synset: str, instance: str) -> list[str]:
    root = Path(surface_root)
    candidates = [
        root / "SurfaceSamples" / "ShapeNetV2" / synset / f"{instance}.ply",
        root / "SurfaceSamples" / "ShapeNetV2" / synset / f"{instance}.npz",
        root / "ShapeNetV2" / synset / f"{instance}.npz",
        root / "ShapeNetV2" / synset / f"{instance}.ply",
        root / synset / f"{instance}.npz",
        root / synset / f"{instance}.ply",
        root / f"{instance}.npz",
        root / f"{instance}.ply",
    ]
    return [str(p) for p in candidates]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default="external_artifacts/remote_deepsdf_setup")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace)
    split_dir = workspace / "DeepSDF" / "examples" / "splits"
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    manifest = {}
    for class_name, meta in CLASSES.items():
        split_path = split_dir / meta["split"]
        if split_path.exists():
            instances = flatten_split(json.loads(split_path.read_text(encoding="utf-8")))
        else:
            instances = []

        csv_path = output / f"{class_name}_official_full_test_inputs.csv"
        rows = []
        for inst in instances:
            candidates = candidate_paths(meta["surface_root"], meta["synset"], inst)
            existing = next((p for p in candidates if Path(p).exists()), "")
            rows.append(
                {
                    "class": class_name,
                    "synset": meta["synset"],
                    "instance": inst,
                    "surface_root": meta["surface_root"],
                    "existing_surface_path": existing,
                    "candidate_paths": "|".join(candidates),
                }
            )
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "class",
                    "synset",
                    "instance",
                    "surface_root",
                    "existing_surface_path",
                    "candidate_paths",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)

        manifest[class_name] = {
            "split_file": str(split_path),
            "synset": meta["synset"],
            "surface_root": meta["surface_root"],
            "count": len(instances),
            "csv": str(csv_path),
            "found_surface_files": sum(1 for row in rows if row["existing_surface_path"]),
        }

    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

