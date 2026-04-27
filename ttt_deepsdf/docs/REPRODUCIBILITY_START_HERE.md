# Reproducibility Start Here

This page is the public entry point for reproducing the project from GitHub.

## What A New Reader Can Do From This Repository

1. Clone the repository and inspect all small, Git-friendly materials: source code, experiment configs, result CSV/JSON summaries, selected figures, and reproduction notes.
2. Reproduce the original airplane DeepSDF workflow from the root `README.md`.
3. Reproduce or extend the three-class TTT/LoRA experiments from `ttt_deepsdf/README.md` and `ttt_deepsdf/docs/REPRODUCTION_GUIDE.md`.
4. Download external data or model/result archives from the two Google Drive folders below when full reruns or audits are needed.

## External Folders

| Need | Folder | Link |
| --- | --- | --- |
| I need the prepared dataset to rerun evaluation/training. | Processed dataset folder | https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=sharing |
| I need checkpoints, meshes, server snapshots, and final archives. | Result/model artifact folder | https://drive.google.com/drive/folders/1EPH4qcBP8OfL0nSVdleFuJZi2a7E6H4a?usp=sharing |

## Minimal Reproduction Route

1. Install dependencies from `ttt_deepsdf/requirements.txt`.
2. Download and extract the processed dataset folder into `ttt_deepsdf/external_artifacts/`.
3. Run the SDF-MAE evaluation commands in `ttt_deepsdf/docs/REPRODUCTION_GUIDE.md`.
4. For full mesh/Chamfer auditing, download the result/model artifact folder or regenerate meshes using the reconstruction commands.
5. Compare generated outputs with the committed summaries in `ttt_deepsdf/results/tables/` and `ttt_deepsdf/results/source_jsons/`.

## What Is Already Committed

- `ttt_deepsdf/results/tables/`: final compact CSV summaries for TTT/LoRA, Chamfer, extra surface metrics, ablation/efficiency, Curriculum/related baselines, and latent-dimension runs.
- `ttt_deepsdf/results/source_jsons/`: compact machine-readable run summaries.
- `ttt_deepsdf/results/deepsdf_latent/`: He Ying latent-dimension assignment outputs.
- `ttt_deepsdf/figures/`: selected qualitative figures, distribution plots, and communication figures.
- `ttt_deepsdf/docs/`: reproduction guide, result summary, baseline context, TTT design notes, and artifact policy.

## What Is Intentionally External

Full ShapeNet-derived processed samples, full checkpoints, full reconstructed meshes, per-shape TTT state files, and cloud/server snapshots are too large for GitHub. They are documented in `DATA_AND_ARTIFACTS.md` and `GOOGLE_DRIVE_ARTIFACT_MANIFEST_2026-04-27.md` instead of being committed directly.