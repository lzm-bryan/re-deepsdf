# Results Summary

The experiments compare a reproduced DeepSDF baseline with parameter-efficient
test-time adaptation methods: residual TTT, LoRA, and LoRA-FA.

## Scope

- Classes: airplane, chair, lamp.
- Checkpoints: 100 and 200.
- Main metrics: SDF-MAE and full-split Chamfer distance.
- Claim boundary: matched-protocol improvement over the reproduced DeepSDF
  baseline, not an external state-of-the-art claim.

## SDF-MAE

From `results/tables/ttt_sdf_mae_summary.csv`, LoRA is the best method in every
completed row.

| Class | Checkpoint | Baseline SDF-MAE | LoRA-TTT SDF-MAE | Relative Improvement |
| --- | ---: | ---: | ---: | ---: |
| airplane | 100 | 0.00748256 | 0.00419800 | 43.9% |
| airplane | 200 | 0.00655049 | 0.00360040 | 45.0% |
| chair | 100 | 0.01083527 | 0.00585965 | 45.9% |
| chair | 200 | 0.01017104 | 0.00501939 | 50.7% |
| lamp | 100 | 0.01327528 | 0.00884076 | 33.4% |
| lamp | 200 | 0.01079664 | 0.00738548 | 31.6% |

## Full-Split Chamfer

From `results/tables/full_chamfer_summary.csv`, LoRA improves the full-class
Chamfer comparison in every completed class/checkpoint setting.

| Class | Checkpoint | Baseline Mean Chamfer | LoRA Mean Chamfer | Relative Improvement | Valid |
| --- | ---: | ---: | ---: | ---: | ---: |
| airplane | 100 | 0.000440772 | 0.000199222 | 54.8% | 456 |
| airplane | 200 | 0.000240659 | 0.000128779 | 46.5% | 456 |
| chair | 100 | 0.000902503 | 0.000429429 | 52.4% | 832 |
| chair | 200 | 0.000682192 | 0.000270965 | 60.3% | 832 |
| lamp | 100 | 0.003141395 | 0.001423707 | 54.7% | 213 |
| lamp | 200 | 0.002060678 | 0.001061194 | 48.5% | 213 |

## Figures

Qualitative selected-case panels are stored in `figures/`:

- `airplane_ckpt100_baseline_vs_lora_selected8_N256.png`
- `chair_ckpt100_baseline_vs_lora_selected8_N256.png`
- `lamp_ckpt100_baseline_vs_lora_selected8_N256.png`
- `communication/qualitative_ckpt200_gt_deepsdf_lora.png`

## Recommended Wording

Use:

> Compared with our reproduced DeepSDF baseline under the same checkpoint and
> evaluation protocol, LoRA-TTT consistently improves reconstruction metrics on
> airplane, chair, and lamp.

Avoid:

> This is state of the art.

That stronger claim would require rerunning external baselines under the same
long-budget protocol.




