# Albert Assignment Writing Draft: DeepSDF With Test-Time Adaptation

Last updated: 2026-04-26 12:20, Asia/Singapore.

## Recommended Title

Parameter-Efficient Test-Time Adaptation for DeepSDF Shape Reconstruction

## One-Sentence Claim

Under the same official ShapeNet class splits and matched 100/200-checkpoint DeepSDF protocol, parameter-efficient LoRA test-time adaptation consistently improves SDF-MAE and full-split Chamfer distance over the reproduced DeepSDF baseline on airplane, chair, and lamp.

## Safe Claim Boundary

Use this wording:

- "Compared with our reproduced DeepSDF baseline under the same checkpoint and evaluation protocol, LoRA-TTT improves reconstruction metrics consistently."
- "The result suggests test-time adaptation is a promising lightweight correction step for implicit shape reconstruction."

Avoid this wording:

- "This is state of the art."
- "This beats all recent 3D reconstruction methods."
- "This reproduces the full long-budget DeepSDF Table-3 benchmark."

The current experiments are strong for a course project and a paper-direction prototype. They are not yet a strict external-SOTA benchmark, because external baselines were not all rerun under the exact same long-budget setting.

## Experimental Setup

Dataset and split:

- ShapeNet airplane, chair, and lamp.
- Official DeepSDF/DeepSTF-style train/test split already used in the local project.
- Main full-split valid counts: airplane 456, chair 832, lamp 213.

Baseline:

- DeepSDF reproduced models at checkpoints 100 and 200.
- Baseline evaluation uses test-time latent optimization with fixed decoder weights.

TTT variants:

- Residual TTT.
- LoRA TTT.
- LoRA-FA TTT.

Main evaluation metrics:

- SDF-MAE on official test samples.
- Full-class Chamfer distance from reconstructed meshes/surfaces.
- Checkpoint-100 extra surface metrics: approximate Sinkhorn EMD, mesh accuracy/completeness, and F-score.
- Runtime/efficiency fields where available.

## Main Quantitative Result

From `results/ttt_sdf_mae_summary.csv`, LoRA is the best method in every completed SDF-MAE row:

| Class | Checkpoint | Baseline SDF-MAE | LoRA-TTT SDF-MAE | Relative Improvement |
| --- | ---: | ---: | ---: | ---: |
| airplane | 100 | 0.00748256 | 0.00419800 | 43.9% |
| airplane | 200 | 0.00655049 | 0.00360040 | 45.0% |
| chair | 100 | 0.01083527 | 0.00585965 | 45.9% |
| chair | 200 | 0.01017104 | 0.00501939 | 50.7% |
| lamp | 100 | 0.01327528 | 0.00884076 | 33.4% |
| lamp | 200 | 0.01079664 | 0.00738548 | 31.6% |

Interpretation:

The gain is not limited to one category or one checkpoint. LoRA-TTT improves all three categories at both 100 and 200 checkpoints, with the largest SDF-MAE gain on chair checkpoint 200 and the most modest but still clear gain on lamp.

## Full-Split Chamfer Result

From `results/full_chamfer_summary.csv`, LoRA also improves full-class Chamfer in all six class/checkpoint settings:

| Class | Checkpoint | Baseline Mean Chamfer | LoRA Mean Chamfer | Relative Improvement | Valid |
| --- | ---: | ---: | ---: | ---: | ---: |
| airplane | 100 | 0.000440772 | 0.000199222 | 54.8% | 456 |
| airplane | 200 | 0.000240659 | 0.000128779 | 46.5% | 456 |
| chair | 100 | 0.000902503 | 0.000429429 | 52.4% | 832 |
| chair | 200 | 0.000682192 | 0.000270965 | 60.3% | 832 |
| lamp | 100 | 0.003141395 | 0.001423707 | 54.7% | 213 |
| lamp | 200 | 0.002060678 | 0.000942479 | 54.3% | 213 |

Interpretation:

The mesh/surface-level result agrees with the SDF-MAE result: the adapted model is not merely overfitting the SDF sample metric, but also improves reconstructed geometry under a full-class surface comparison.

## Extra Surface Metrics

From `results/full_extra_surface_metrics_summary.csv`, checkpoint-100 extra metrics provide additional evidence beyond MAE and Chamfer:

- Chair: mesh accuracy improves from 0.0116418 to 0.00811142, approximate Sinkhorn EMD improves from 0.0656351 to 0.0578656, and F@0.005 improves from 0.2991 to 0.3772.
- Lamp: mesh accuracy improves from 0.0172961 to 0.00994312, approximate Sinkhorn EMD improves from 0.101316 to 0.0723828, and F@0.005 improves from 0.3438 to 0.4483.
- Airplane: mesh accuracy improves from 0.00676042 to 0.00452577, approximate Sinkhorn EMD improves from 0.0477330 to 0.0407298, and F@0.005 improves from 0.6602 to 0.7467.

Use "approximate Sinkhorn EMD" rather than "exact EMD" in the report.

## Qualitative Figures To Use

Use the selected-8 baseline-vs-LoRA panels:

- `figures/airplane_ckpt100_baseline_vs_lora_selected8_N256.png`
- `figures/chair_ckpt100_baseline_vs_lora_selected8_N256.png`
- `figures/lamp_ckpt100_baseline_vs_lora_selected8_N256.png`

Suggested caption:

"Selected test reconstructions at checkpoint 100. For each class, the LoRA-TTT reconstructions better preserve the target geometry than the reproduced DeepSDF baseline, matching the quantitative improvements in SDF-MAE and Chamfer distance."

## Suggested Report Structure

1. Motivation: DeepSDF is a strong implicit reconstruction baseline, but fixed decoders can leave systematic residual errors at test time.
2. Method: Add parameter-efficient test-time adaptation, especially LoRA, while preserving the pretrained DeepSDF decoder structure.
3. Protocol: Same data splits, same categories, same checkpoints, and paired baseline-vs-TTT evaluation.
4. Results: Present SDF-MAE table first, full Chamfer table second, extra surface metrics third.
5. Efficiency: Report that LoRA is parameter-efficient and compare residual/LoRA/LoRA-FA from the efficiency table.
6. Qualitative analysis: Show selected-8 panels.
7. Limitations: No external SOTA claim; approximate EMD; checkpoint 100/200 practical budget rather than full long-budget DeepSDF reproduction.
8. Conclusion: LoRA-TTT is a stable, lightweight improvement over the reproduced DeepSDF baseline.

## Final Checklist Before Submission

- Include `ttt_sdf_mae_summary.csv` and `full_chamfer_summary.csv` in the report or appendix.
- Mention that LoRA is best in all six SDF-MAE rows.
- Mention full Chamfer improves in all six rows.
- Label EMD as approximate Sinkhorn EMD.
- Do not claim external SOTA.
- Put raw paths in appendix if the teacher wants reproducibility.

