# Albert Checkpoint-200 Extra Surface Metrics

Generated: 2026-04-26 14:08:33

Source: `results/ckpt200_extra_surface_metrics_summary.csv`.

Lower is better for accuracy, Chamfer-L1, and approximate Sinkhorn EMD. Higher is better for F-score.

| Class | Valid | Accuracy improvement | Chamfer-L1 improvement | Sinkhorn EMD improvement | F@0.005 improvement | F@0.01 improvement |
|---|---:|---:|---:|---:|---:|---:|
| airplane | 456 | 23.1% | 19.1% | 8.8% | 9.4% | 4.2% |
| chair | 832 | 30.9% | 26.4% | 12.0% | 25.0% | 12.6% |
| lamp | 213 | 42.9% | 34.7% | 21.0% | 28.0% | 16.3% |

Reading: LoRA-TTT improves checkpoint-200 surface metrics for all three classes under the local recomputation protocol. Use "approximate Sinkhorn EMD" wording, not exact EMD.

Artifacts:
- `results/quick_postprocess/albert_ckpt200_extra_surface_improvement_scoreboard.csv`
- `results/quick_postprocess/albert_ckpt200_extra_surface_scoreboard.md`