# Local RTX 5070 NKSR Baseline Plan

Updated: 2026-04-25, Asia/Singapore.

## Goal

Run NKSR as the first external SOTA-style context baseline for the DeepSDF/TTT
paper direction on the three local ShapeNet categories:

- airplane, `02691156`, official test count `456`;
- chair, `03001627`, official test count `832`;
- lamp, `03636649`, official test count `213`.

The goal is not to replace the matched DeepSDF-vs-LoRA table. NKSR should be a
separate external-context comparison because it reconstructs from point clouds,
while DeepSDF/TTT uses the DeepSDF latent/SDF test-time protocol.

## Current Local Environment Status

Environment created:

`external_artifacts/local_conda/envs/nksr-baseline`

Verified working:

- Python `3.10`;
- PyTorch `2.7.0+cu128`;
- RTX 5070 CUDA visibility;
- `torch-scatter 2.1.2+pt27cu128`;
- CUDA `nvcc 12.8` installed inside the conda environment.

Current blocker:

- Native Windows package build failed.
- NKSR package setup prints: `This repository only supports x86-64 Linux!`
- The local machine currently does not have WSL installed.

Conclusion:

> Do not continue trying to build NKSR in native Windows. The next local route
> is WSL2/Linux with NVIDIA CUDA passthrough, or running NKSR on a Linux cloud
> server. The current Windows conda environment is useful evidence that PyTorch
> and CUDA work on the RTX 5070, but it is not enough to run NKSR itself.

## Local Data Manifest Status

Generated under:

`data_manifests`

Files:

- `airplane_official_full_test_inputs.csv`: `456/456` SurfaceSamples found.
- `chair_official_full_test_inputs.csv`: `832/832` SurfaceSamples found.
- `lamp_official_full_test_inputs.csv`: `213/213` SurfaceSamples found.
- `manifest.json`: summary of all three classes.

These manifests point to local `SurfaceSamples` PLY files and can be reused from
WSL or copied to a Linux server.

## Metrics To Report

For SOTA-style external surface reconstruction comparison, use:

| Metric | Use | Notes |
| --- | --- | --- |
| Chamfer Distance / Chamfer-L1 | Primary geometry metric | Already used in our DeepSDF/LoRA pipeline, so this is the best bridge metric. |
| Normal Consistency | Surface quality metric | Common in Occupancy Networks / ConvONet style evaluations; useful if generated meshes have reliable normals. |
| F-score | Boundary/threshold metric | Common in ConvONet-style tables; threshold must be stated. |
| IoU | Optional | Requires watertight occupancy evaluation and consistent sampling; less direct for NKSR unless we implement the occupancy evaluator carefully. |

Recommended paper table:

1. Main matched table: DeepSDF baseline vs residual TTT vs LoRA vs LoRA-FA using
   SDF-MAE and full Chamfer where available.
2. External context table: NKSR using Chamfer, Normal Consistency, and possibly
   F-score on the same three ShapeNet test splits.

## Expected Costs If Running Locally Through WSL2

Assumptions:

- WSL2 Ubuntu with NVIDIA CUDA passthrough works.
- Use NKSR pretrained/kitchen-sink reconstruction or a direct point-cloud
  reconstruction path.
- Input point clouds are generated from our local SurfaceSamples PLY files.
- Start with `3k` oriented points per shape; reduce if memory is tight.

| Stage | Disk Cost | Time Estimate |
| --- | ---: | ---: |
| Install WSL2 + Ubuntu + CUDA access | `8-15 GB` | `0.5-2 h`, may require reboot/admin |
| Install NKSR Linux conda env | `8-15 GB` | `1-3 h` |
| Prepare point-cloud inputs | `1-5 GB` | `10-40 min` |
| Lamp smoke test | small | `10-30 min` |
| Lamp full test, 213 shapes | `0.5-2 GB` outputs | `0.5-2 h` |
| Airplane full test, 456 shapes | `1-4 GB` outputs | `1-3 h` |
| Chair full test, 832 shapes | `2-6 GB` outputs | `2-5 h` |
| Evaluate all meshes | small | `0.5-2 h` |

Total likely time after WSL is ready:

`4-12 h` for all three classes, depending on point count, mesh extraction
resolution, and whether evaluation runs cleanly.

Total extra disk needed:

`20-40 GB` is a safer budget. The current C drive has roughly `41 GB` free
after the native Windows environment setup, so it is possible but tight.

## Recommended Execution Order

1. Do not install the other three external baselines yet.
2. Decide whether to enable WSL2 locally or run NKSR on a Linux server.
3. If WSL2 is enabled, run lamp first.
4. Use the same local Chamfer evaluator used for DeepSDF/LoRA outputs.
5. Only after lamp is valid, run airplane and chair.
6. Keep NKSR in a separate external-context table.

## Claim Boundary

Safe claim after NKSR runs:

> We compare against a modern point-cloud surface reconstruction baseline
> (NKSR) on the same ShapeNet test categories using the same mesh evaluator.

Avoid:

> Our method is globally SOTA.

That claim would still need full metric alignment, input-protocol clarity, and
possibly EMD / mesh accuracy / normal consistency across all compared methods.



