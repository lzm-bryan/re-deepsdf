# He Ying Assignment: DeepSDF Reproduction and Latent-Dimension Study

Last refreshed: 2026-04-26 12:20, Asia/Singapore.

## Goal

Reproduce DeepSDF behavior and study latent code dimension as the controlled
variable.

## Current Result Table

`results\latent_metrics_summary.csv`

## Writing Draft

Use this file to write the final report:

`HE_YING_WRITING_DRAFT_2026-04-26.md`

## Current Status

- Airplane: latent dimensions `64`, `128`, and `256` complete at checkpoint `100`.
- Lamp: latent dimensions `64`, `128`, and `256` complete at checkpoint `100`.
- Chair local RTX 5070 queue: chair 64: quick_eval_complete, 100/100 epochs; chair 128: quick_eval_complete, 100/100 epochs; chair 256: quick_eval_complete, 100/100 epochs.

Chair `64/128/256` currently use a 128-shape quick-eval subset. Chair full
official eval is optional polish, not required for the current He Ying report if
the scope is labeled clearly.

## Important Assets

- `results\source_jsons`: source summaries from cloud runs.
- `results\chair_local_status`: local chair queue and quick-eval status.
- `figures\distribution_outputs`: latent PCA/norm distribution assets.
- `figures\airplane_qualitative_recon_500.png`
- `figures\airplane_latent_interpolation_500.png`
- `notes`: split, preprocessing, and assignment-alignment notes.

Large data and checkpoints remain in the shared workspace, not this folder.
