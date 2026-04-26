# TTT-DeepSDF Results And Reproduction Package

This folder contains the small, Git-friendly artifact package for the
DeepSDF test-time adaptation experiments. It includes the TTT evaluation code,
curated result tables, qualitative figures, and reproduction notes.

Large data, checkpoints, reconstructed meshes, and per-shape TTT state files are
not stored in Git. They should be downloaded separately and unpacked under
`external_artifacts/` as described in `docs/DATA_AND_ARTIFACTS.md`.

## What Is Included

- `scripts/`: reusable TTT evaluation and mesh-reconstruction scripts.
- `baselines/`: DeepSDF reference code, Curriculum DeepSDF code, and external
  baseline staging docs/scripts.
- `results/tables/`: paper/report-facing CSV summaries.
- `results/deepsdf_latent/`: DeepSDF latent-dimension reproduction results.
- `results/deepsdf_planes_600epoch/`: note for the original airplane DeepSDF
  reproduction artifacts.
- `results/source_jsons/`: sanitized machine-readable summaries from the runs.
- `results/selected_cases/`: selected-case CSV/JSON manifests.
- `figures/`: small qualitative and summary figures.
- `docs/`: reproduction guide, artifact policy, and result summary.
- `configs/`: example command configuration.

## Main Result

LoRA test-time adaptation improves over the reproduced DeepSDF baseline on all
completed SDF-MAE and full-split Chamfer comparisons for airplane, chair, and
lamp at checkpoints 100 and 200. See `docs/RESULTS_SUMMARY.md` for the compact
tables and claim boundary.

## Quick Start

Install dependencies:

```bash
pip install -r ttt_deepsdf/requirements.txt
```

Run a LoRA SDF-MAE evaluation after downloading the external artifacts:

```bash
python ttt_deepsdf/scripts/evaluate_sdf_ttt.py \
  --deepsdf-dir source_code/src \
  --experiment external_artifacts/experiments/airplane_code256_e200 \
  --checkpoint 200 \
  --data-root external_artifacts/data \
  --split-file external_artifacts/splits/sv2_planes_test.json \
  --mode lora \
  --iters 100 \
  --output-subdir EvaluationTTT \
  --output-name lora_summary_200.json
```

For full mesh reconstruction and Chamfer evaluation, see
`docs/REPRODUCTION_GUIDE.md`.

## Data Link Placeholder

The three-class processed data bundle link can be added here after upload:

```text
Google Drive folder:
https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=drive_link
```

Recommended location in this package:

- short link and checksums: `docs/DATA_AND_ARTIFACTS.md`
- optional mirrored note: this README



