# Reproduction Guide

This guide reproduces the main DeepSDF baseline versus TTT comparisons after the
external data and checkpoint artifacts are downloaded.

## 1. Environment

Create a Python environment with PyTorch and the required packages:

```bash
pip install -r ttt_deepsdf/requirements.txt
```

For GPU runs, install the PyTorch build that matches your CUDA version.

## 2. Artifacts

Download the external artifacts and unpack them under:

```text
ttt_deepsdf/external_artifacts/
```

See `DATA_AND_ARTIFACTS.md` for the expected layout. A DeepSDF experiment must
contain `specs.json`, `ModelParameters/<checkpoint>.pth`, and
`LatentCodes/<checkpoint>.pth`.

## 3. Baseline SDF-MAE

```bash
python ttt_deepsdf/scripts/evaluate_sdf_latent_opt.py \
  --deepsdf-dir source_code/src \
  --experiment ttt_deepsdf/external_artifacts/experiments/airplane_code256_e200 \
  --checkpoint 200 \
  --data-root ttt_deepsdf/external_artifacts/data \
  --split-file ttt_deepsdf/external_artifacts/splits/sv2_planes_test.json \
  --output ttt_deepsdf/external_artifacts/runs/airplane_baseline_200.json \
  --iters 200 \
  --samples 4096 \
  --adapt-samples 4096
```

## 4. LoRA TTT SDF-MAE

```bash
python ttt_deepsdf/scripts/evaluate_sdf_ttt.py \
  --deepsdf-dir source_code/src \
  --experiment ttt_deepsdf/external_artifacts/experiments/airplane_code256_e200 \
  --checkpoint 200 \
  --data-root ttt_deepsdf/external_artifacts/data \
  --split-file ttt_deepsdf/external_artifacts/splits/sv2_planes_test.json \
  --mode lora \
  --lora-rank 8 \
  --lora-alpha 16 \
  --lora-layers 0,1,2,3,4,5,6,7 \
  --iters 100 \
  --samples 4096 \
  --adapt-samples 4096 \
  --output-subdir EvaluationTTT \
  --output-name lora_summary_200.json
```

Use `--mode residual` or `--mode lora-fa` to reproduce the other TTT variants.

## 5. Mesh Reconstruction And Chamfer

```bash
python ttt_deepsdf/scripts/reconstruct_ttt_adapted_meshes.py \
  --deepsdf-dir source_code/src \
  --experiment ttt_deepsdf/external_artifacts/experiments/airplane_code256_e200 \
  --checkpoint 200 \
  --data-root ttt_deepsdf/external_artifacts/data \
  --surface-root ttt_deepsdf/external_artifacts/surface_data \
  --split-file ttt_deepsdf/external_artifacts/splits/sv2_planes_test.json \
  --mode lora \
  --output-label PaperLoRA200_Full_N256_i100 \
  --resolution 256 \
  --iters 100 \
  --samples 4096 \
  --adapt-samples 4096
```

For chair and lamp, change the experiment directory and split file:

```text
chair: sv2_chairs_test.json, chair_code256_e100/e200
lamp:  sv2_lamps_test.json,  lamp_code256_e100/e200
```

## 6. Report Tables

The curated results used for writing are already stored in:

```text
ttt_deepsdf/results/tables/
```

The most important files are:

- `ttt_sdf_mae_summary.csv`
- `full_chamfer_summary.csv`
- `full_extra_surface_metrics_summary.csv`
- `efficiency_and_ablation_summary.csv`




