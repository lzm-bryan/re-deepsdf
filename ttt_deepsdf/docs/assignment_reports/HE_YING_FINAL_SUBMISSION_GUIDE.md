# He Ying Final Submission Guide

Last refreshed: 2026-04-25 21:25, Asia/Singapore.

## Final Positioning

This folder is the clean archive for the He Ying assignment version of the DeepSDF project. The assignment should be framed as:

> A DeepSDF reproduction and controlled latent-code dimension study on ShapeNet airplane, lamp, and chair.

The main story is not TTT. The main story is that latent code dimension is varied while the DeepSDF setup is kept fixed.

## Requirement Checklist

| Requirement from teacher/course feedback | Local evidence | Status |
| --- | --- | --- |
| Reproduce DeepSDF behavior | `code\DeepSDF`, complete data, checkpoint-100 experiments | Done |
| Study one controlled variable | latent code dimension `64/128/256` | Done |
| Keep notes on environment and preprocessing | `START_HERE.md`, `notes\DATA_PIPELINE_GUIDE.md`, `notes\DATA_INVENTORY_AND_VERIFICATION_2026-04-25.md` | Done |
| Provide quantitative comparison | `results\latent_metrics_summary.csv` | Done |
| Include consistent visuals | airplane recon/interpolation, latent distribution figures | Mostly done |
| Discuss fine details/thin structures | chair quick-eval rows support the discussion | Done quantitatively; visual chair panel optional |
| Be reproducible for another agent/person | root index, data guide, result CSVs, configs | Done |

## Quantitative Evidence To Use

Primary metric: `test_opt_mae`, lower is better.

| Class | Evaluation scope | Dim 64 | Dim 128 | Dim 256 | Conclusion |
| --- | --- | ---: | ---: | ---: | --- |
| airplane | full official test split, `456` shapes | `0.0106193` | `0.00909968` | `0.00746194` | `256` best |
| lamp | full official test split, `213` shapes | `0.0164145` | `0.0150933` | `0.0132753` | `256` best |
| chair | quick subset, `128` shapes | `0.0200741` | `0.0184119` | `0.0132381` | `256` best |

Suggested wording:

> The results show a consistent decrease in reconstruction MAE as the latent code dimension increases. The trend appears in airplane, lamp, and chair, suggesting that the latent code capacity is an important factor in DeepSDF reconstruction quality.

## Suggested Figures

Use these first:

- `figures\airplane_qualitative_recon_500.png`
- `figures\airplane_latent_interpolation_500.png`
- `figures\distribution_outputs\latent_norm_distribution_all_classes.png` if present, otherwise use the per-class norm/PCA figures in the same folder.

If more time is available, the most useful extra figure would be a chair `64/128/256` visual comparison on thin legs or backrests. It is optional because the quantitative chair result is already complete, but it would match the teacher's feedback especially well.

## Report Boundary

Safe claims:

- DeepSDF reproduction pipeline is runnable and documented locally.
- Latent dimension is studied as the controlled variable.
- Larger latent dimensions improved `test_opt_mae` in all completed categories.
- Chair results are useful for fine-structure discussion but are from a quick subset.

Avoid these claims:

- Full official DeepSDF benchmark reproduction.
- SOTA comparison.
- TTT as the main contribution of this assignment version.

## If Another Agent Continues

1. Read root `START_HERE.md`.
2. Read this file and `README.md` in this folder.
3. Use `results\latent_metrics_summary.csv` for the table.
4. Use `figures` for visuals.
5. If improving the submission, generate a chair thin-structure visual panel, but do not rerun training unless the user asks.
