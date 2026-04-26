# DeepSDF Airplane Reconstruction - 4.13 Planes, 600 Epochs

[中文](README.md) | [English](README.en.md)

> Version: planes, 600 epochs
> Date: 2026-04-13
> Model: DeepSDF Auto-Decoder
> Dataset: ShapeNet V2 airplane class (`02691156`)

---

## Project Map

This repository contains the base DeepSDF reproduction, data-processing notes,
and later TTT/LoRA extension experiments. Use the table below to find the right
entry point.

| Goal | Start Here | Notes |
| --- | --- | --- |
| Run the base DeepSDF airplane reconstruction | This README | Environment setup, data links, inference, visualization, training, and evaluation. |
| Understand how the data was collected or processed | [`数据处理复现/`](数据处理复现/README.en.md) | Historical data-processing notes, CPU/server reproduction notes, reference links, and offline webpage backups. Most readers can skip this first. |
| Read the TTT / LoRA DeepSDF extension | [`ttt_deepsdf/`](ttt_deepsdf/) | TTT code, DeepSDF/TTT result tables, figures, reproduction guide, Curriculum DeepSDF notes, and SOTA baseline planning docs. |

Recommended reading order for new users: first run the base reproduction from
this README; read `数据处理复现/README.en.md` only when tracing data provenance; go to
`ttt_deepsdf/README.md` for the TTT/LoRA research package.

## Repository Layout

```text
re-deepsdf/
├── configs/           # DeepSDF airplane experiment config
├── generated/         # small generated mesh examples
├── images/            # visualization images
├── models/            # small model and latent-code examples
├── scripts/           # generation, rendering, and visualization scripts
├── source_code/       # DeepSDF training, reconstruction, and evaluation code
├── ttt_deepsdf/       # TTT/LoRA DeepSDF research package
└── 数据处理复现/      # data-processing notes and reference materials
```

Large datasets, full checkpoints, and full reconstruction meshes are not meant
to be stored directly in Git. Download them from the Google Drive links in this
README or `ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md`.

---

## Quick Inference Run

```bash
# 1. Clone this repository
git clone https://github.com/lzm-bryan/re-deepsdf.git
cd re-deepsdf

# 2. Download data
# Download and extract the data/ folder from Google Drive. See links below.

# 3. Generate new airplane meshes
python scripts/generate_new_planes.py -n 5

# 4. Visualize one generated mesh
python scripts/visualize_compare.py single generated/GeneratedPlanes/generated_plane_001.ply
```

---

## Full Training Reproduction

Training reproduction is optional if you only want to inspect the provided model
and generated samples.

### Environment

```bash
pip install torch numpy trimesh matplotlib scikit-image open3d
# or
conda install pytorch numpy trimesh matplotlib scikit-image
```

### Data Preparation

Download and extract the data into the repository-level `data/` directory.

| Artifact | Size | Description | Link |
| --- | ---: | --- | --- |
| Training data | 4.1 GB | Full training `SdfSamples` and `NormalizationParameters` | [train_4.13planes-600epoch.zip](https://drive.google.com/file/d/1KCqG-tOYm3H92792S17m-JFwLCmFdS0k/view?usp=sharing) |
| Test data | 3.0 GB | Test SDF samples and normalization parameters | [test_4.13planes-600epoch.zip](https://drive.google.com/file/d/19ENGz3Cnxp_7HmjjBLcPgkSR23UpwqC-/view?usp=sharing) |
| Reconstructions | 261 MB | 456 reconstructed meshes | [reconstructions_4.13planes-600epoch.zip](https://drive.google.com/file/d/11KQy6ca7o8MuPxGZBU5PWwAhzOVQhw9n/view?usp=sharing) |
| Latent codes | 583 KB | Latent codes for 627 training shapes | [latentcodes_4.13planes-600epoch.zip](https://drive.google.com/file/d/1WeusBcG0clPVxzfozuSA0M84I8EKtSN7/view?usp=sharing) |

Expected layout after extraction:

```text
data/
├── SdfSamples/ShapeNetV2/02691156/
├── NormalizationParameters/ShapeNetV2/02691156/
├── TestData/SdfSamples/ShapeNetV2/02691156/
└── TestData/NormalizationParameters/ShapeNetV2/02691156/
```

### Alternative: Generate Data From ShapeNet

1. Register and download ShapeNet V2 from <https://shapenet.org/>.
2. Download class `02691156` for airplanes.
3. Generate DeepSDF samples:

```bash
python source_code/src/generate_training_meshes.py \
    --data-source /path/to/shapenet \
    --shape-category 02691156 \
    --output-dir ./data/SdfSamples
```

### Config

`configs/specs.json` contains the default relative-path configuration for the
airplane experiment.

### Training

```bash
python source_code/src/train_deep_sdf.py \
    --experiment-name planes_600epoch \
    --data-path ./data \
    --epochs 600
```

### Evaluation

```bash
# Reconstruct the test set
python source_code/src/reconstruct.py \
    --experiment-name planes_600epoch \
    --checkpoint models/ModelParameters/600.pth

# Compute metrics
python source_code/src/evaluate.py \
    --experiment-name planes_600epoch \
    --reconstruction-dir ./data/Reconstructions
```

---

## Data Format

Each `.npz` SDF sample contains:

- `pos`: positive samples with shape `N x 4`, formatted as `[x, y, z, sdf]`
- `neg`: negative samples with shape `M x 4`, formatted as `[x, y, z, sdf]`

---

## Model Summary

The decoder is an auto-decoder DeepSDF network:

```python
Decoder(
    latent_size=256,
    dims=[512 x 8],
    latent_in=[4],
    dropout=[0-7],
    weight_norm=True,
)
```

Training strategy:

| Parameter | Value |
| --- | ---: |
| Batch size | 4 scenes |
| Samples per scene | 16384 |
| Initial learning rate | 0.0005 |
| LR schedule | Step, halve every 500 epochs |
| Code regularization | 1e-4 |

DeepSDF is an auto-decoder: each training shape owns a learnable latent vector,
and the decoder maps `latent + xyz` to an SDF value.

---

## Utility Scripts

Generate new airplanes:

```bash
python scripts/generate_new_planes.py -n 5
python scripts/generate_new_planes.py -n 10 -o my_output
```

Visualize meshes:

```bash
python scripts/visualize_compare.py single file.ply
python scripts/visualize_compare.py
python scripts/visualize_compare.py compare mesh1.ply mesh2.ply
```

Render multiple views:

```bash
python scripts/render_planes.py
```

---

## TTT / LoRA Extension

The later TTT/LoRA research package is under:

```text
ttt_deepsdf/
```

It includes DeepSDF-vs-TTT result tables, small figures, TTT evaluation scripts,
Curriculum DeepSDF code notes, and future SOTA baseline planning documents.
Large three-class artifacts are hosted outside Git:

```text
https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=drive_link
```

Start with `ttt_deepsdf/README.md`.

---

## Current Airplane Result

| Metric | Value |
| --- | ---: |
| Test samples | 456 |
| Chamfer Distance (x1000) | about 0.36 |
| Reconstruction completion | 100% |

Example figures:

| File | Description |
| --- | --- |
| `images/generated_planes_view.png` | six generated airplanes |
| `images/generated_vs_real.png` | generated-vs-real comparison |
| `images/renders/*.png` | four-view renders for individual airplanes |

---

## FAQ

### Out of memory?

Reduce the batch size in `specs.json`, for example:

```json
"ScenesPerBatch": 2
```

### Training is slow?

Use a GPU and consider reducing `SamplesPerScene` to `8192` for a faster first
run.

### Generated quality is poor?

Train for more epochs and/or use a higher marching-cubes resolution such as
`N=256`.

### How do I inspect training progress?

```bash
python scripts/plot_log.py --log models/Logs/Logs.pth
```

---

## Future Directions

1. Longer training, such as 1000+ epochs.
2. Higher marching-cubes resolution, such as 256 or 512.
3. More ShapeNet categories.
4. Conditional DeepSDF generation.
5. Latent interpolation and shape morphing.
