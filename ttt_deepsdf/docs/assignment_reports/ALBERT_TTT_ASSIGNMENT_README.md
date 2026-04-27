# Albert Assignment and Paper Direction: TTT/LoRA DeepSDF Improvement

Last refreshed: 2026-04-27 03:48, Asia/Singapore.

## Goal

Use DeepSDF as the fair baseline and evaluate parameter-efficient test-time
adaptation: residual TTT, LoRA, and LoRA-FA.

## Main Tables

- `results\ttt_sdf_mae_summary.csv`
- `results\selected8_chamfer_summary.csv`
- `results\full_chamfer_summary.csv`
- `results\full_extra_surface_metrics_summary.csv`
- `results\efficiency_and_ablation_summary.csv`

## Writing Draft

Use this file to write the final report:

`ALBERT_TTT_WRITING_DRAFT_2026-04-26.md`

## Current Completion State

- Three-class SDF-MAE comparisons are complete for checkpoint `100` and `200`.
- LoRA is the best TTT method in every completed SDF-MAE row.
- Selected-8 Chamfer comparisons are complete for all three classes at
  checkpoint `100`.
- Full official-split Chamfer comparisons are complete for all three classes at
  checkpoints `100` and `200`.
- Checkpoint-100 extra surface metrics are complete for all three classes:
  approximate Sinkhorn EMD, mesh accuracy/completeness, and F-score.
- Efficiency/ablation table now includes lamp ablations, chair LoRA efficiency,
  and airplane checkpoint-200 residual/LoRA/LoRA-FA efficiency rows.

## Claim Boundary

The current archive supports a strong matched DeepSDF-vs-TTT course/paper
direction. It still should not claim external SOTA, because the experiments are
100/200-epoch practical matched-protocol runs rather than a full long-budget
reproduction of every current SOTA baseline.

## Server Sources

- `server_snapshots\30446`: lamp, He Ying, distribution, and paper-metric results.
- `server_snapshots\30622`: chair/airplane TTT queues and selected-case outputs.

Large data and raw checkpoints remain in the shared workspace and
`server_snapshots`.


## Latest Curriculum Baseline Sync

- Chair CurriculumDeepSDF-fullish e100 is now synced from 30622: SDF-MAE 0.0110698863, mean Chamfer 0.0010901162, median Chamfer 0.0004982238.
- Airplane CurriculumDeepSDF-fullish e200 is synced from 30622: SDF-MAE 0.0066488076, mean Chamfer 0.0004079006, median Chamfer 0.0001052846.
- Chair CurriculumDeepSDF-fullish e200 completed on 30446 before reboot with mean Chamfer 0.0018420460 and median Chamfer 0.0004092515, but full source artifact sync is pending until 30446 is reachable.
