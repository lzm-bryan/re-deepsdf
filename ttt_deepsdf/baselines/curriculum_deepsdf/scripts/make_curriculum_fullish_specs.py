#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-spec", required=True)
    ap.add_argument("--out-exp", required=True)
    ap.add_argument("--class-name", required=True)
    ap.add_argument("--num-epochs", type=int, default=200)
    args = ap.parse_args()

    src = Path(args.source_spec)
    out = Path(args.out_exp)
    out.mkdir(parents=True, exist_ok=True)
    specs = json.loads(src.read_text(encoding="utf-8"))
    specs["Description"] = (
        f"CurriculumDeepSDF-fullish {args.class_name} e{args.num_epochs}: "
        "compute-limited vertical baseline using epsilon tolerance loss and "
        "hard/semi-hard/easy sample weighting; fixed decoder, no progressive layer growth."
    )
    specs["NumEpochs"] = args.num_epochs
    specs["SnapshotFrequency"] = args.num_epochs
    snapshots = [10, 50, args.num_epochs]
    if args.num_epochs >= 100:
        snapshots.append(100)
    specs["AdditionalSnapshots"] = sorted(set(snapshots))
    specs["LogFrequency"] = 5
    specs["CurriculumFullish"] = {
        "Enabled": True,
        "Name": "CurriculumDeepSDF-fullish",
        "EpsilonStart": 0.01,
        "EpsilonEnd": 0.001,
        "HardWeightStart": 1.0,
        "HardWeightEnd": 2.5,
        "SemiHardWeightStart": 1.0,
        "SemiHardWeightEnd": 1.5,
        "EasyWeightStart": 1.0,
        "EasyWeightEnd": 0.8,
        "NearSurfaceBand": 0.02,
        "Omitted": "Progressive layer growth is omitted to preserve the existing DeepSDF decoder and keep a controlled comparison.",
    }
    (out / "specs.json").write_text(json.dumps(specs, indent=2), encoding="utf-8")
    print(out / "specs.json")


if __name__ == "__main__":
    main()

