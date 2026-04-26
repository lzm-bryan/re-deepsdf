# He Ying Latent-Dimension Quick Summary

Generated: 2026-04-26 13:33:43

| Class | Test count | MAE@64 | MAE@128 | MAE@256 | Best dim | 64->256 improvement |
|---|---:|---:|---:|---:|---:|---:|
| airplane | 456 | 0.010619 | 0.009100 | 0.007462 | 256 | 29.7% |
| chair | 832 | 0.019826 | 0.018219 | 0.013147 | 256 | 33.7% |
| lamp | 213 | 0.016415 | 0.015093 | 0.013275 | 256 | 19.1% |

Main reading: in all three categories, CodeLength=256 has the lowest test-opt SDF MAE under the current setting.

Artifacts:
- results/quick_postprocess/he_ying_latent_trend_scoreboard.csv
- figures/quick_postprocess/he_ying_latent_dim_trend.svg


