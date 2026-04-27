# Albert / TTT Quick Scoreboard

Generated: 2026-04-26 13:33:43

## Full Chamfer: LoRA vs baseline

| Class | Ckpt | Count | Baseline Chamfer | LoRA Chamfer | Improvement |
|---|---:|---:|---:|---:|---:|
| airplane | 100 | 456 | 0.000441 | 0.000199 | 54.8% |
| airplane | 200 | 456 | 0.000241 | 0.000129 | 46.5% |
| chair | 100 | 832 | 0.000903 | 0.000429 | 52.4% |
| chair | 200 | 832 | 0.000682 | 0.000271 | 60.3% |
| lamp | 100 | 213 | 0.003141 | 0.001424 | 54.7% |
| lamp | 200 | 213 | 0.002061 | 0.000942 | 54.3% |

## SDF MAE: best TTT variant vs baseline

| Class | Ckpt | Best method | Baseline MAE | Best MAE | Improvement |
|---|---:|---|---:|---:|---:|
| airplane | 100 | lora | 0.007483 | 0.004198 | 43.9% |
| airplane | 200 | lora | 0.006550 | 0.003600 | 45.0% |
| chair | 100 | lora | 0.010835 | 0.005860 | 45.9% |
| chair | 200 | lora | 0.010171 | 0.005019 | 50.7% |
| lamp | 100 | lora | 0.013275 | 0.008841 | 33.4% |
| lamp | 200 | lora | 0.010797 | 0.007385 | 31.6% |

Artifacts:
- results/quick_postprocess/albert_full_chamfer_improvement_scoreboard.csv
- figures/quick_postprocess/albert_full_chamfer_lora_improvement.svg
- figures/quick_postprocess/albert_ttt_sdf_mae_improvement.svg