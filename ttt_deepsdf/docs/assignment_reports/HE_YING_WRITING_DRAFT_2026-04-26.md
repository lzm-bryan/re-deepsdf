# He Ying Assignment Writing Draft: DeepSDF Reproduction And Latent Dimension Study

Last updated: 2026-04-26 12:20, Asia/Singapore.

## Recommended Title

Reproducing DeepSDF and Studying Latent Code Dimensionality for 3D Shape Reconstruction

## One-Sentence Claim

Using the reproduced DeepSDF pipeline, increasing latent code dimensionality from 64 to 256 consistently improves test-time optimized SDF-MAE on airplane, lamp, and the chair quick-evaluation subset.

## Safe Claim Boundary

Use this wording:

- "The experiment reproduces the DeepSDF workflow and studies the effect of latent code dimensionality."
- "Larger latent codes improve reconstruction error in the tested settings."
- "Chair is reported as a quick-evaluation subset, while airplane and lamp use the full official test split."

Avoid this wording:

- "The chair result is a full official chair benchmark."
- "The experiment proves 256 dimensions is always optimal."
- "This is a full reproduction of every DeepSDF benchmark number."

## Experimental Setup

Models:

- DeepSDF decoders trained with latent code dimensions 64, 128, and 256.
- Main checkpoint used in the assignment summary: checkpoint 100.

Data:

- Airplane: full official test split, 456 valid test shapes.
- Lamp: full official test split, 213 valid test shapes.
- Chair: local quick-evaluation subset, 128 valid test shapes.

Metrics:

- Train SDF-MAE where available.
- Test mean SDF-MAE.
- Test-time optimized SDF-MAE.

Main result file:

- `results/latent_metrics_summary.csv`

## Main Quantitative Result

From `results/latent_metrics_summary.csv`:

| Class | Test Scope | Latent 64 Test-Opt MAE | Latent 128 Test-Opt MAE | Latent 256 Test-Opt MAE | 64-to-256 Improvement |
| --- | --- | ---: | ---: | ---: | ---: |
| airplane | official full test | 0.01061929 | 0.00909968 | 0.00746194 | 29.7% |
| lamp | official full test | 0.01641454 | 0.01509333 | 0.01327528 | 19.1% |
| chair | quick 128-shape subset | 0.02007408 | 0.01841185 | 0.01323811 | 34.1% |

Interpretation:

The same trend appears across all reported classes: the 256-dimensional latent code gives the lowest test-time optimized SDF-MAE. This supports the expected DeepSDF behavior that a higher-dimensional latent space can encode more shape variation, especially when optimized per test instance.

## Figures To Use

Recommended main figures:

- `figures/airplane_qualitative_recon_500.png`
- `figures/airplane_latent_interpolation_500.png`
- `figures/distribution_outputs/latent_norm_distribution.svg`
- `figures/distribution_outputs/airplane_code64_latent_pca.svg`
- `figures/distribution_outputs/airplane_code128_latent_pca.svg`
- `figures/distribution_outputs/airplane_code256_latent_pca.svg`

Suggested qualitative caption:

"Qualitative DeepSDF reconstructions and latent interpolation on the airplane category. The interpolation result shows that the learned latent space supports smooth shape transitions, while the quantitative table shows lower test-time optimized SDF-MAE with larger latent dimensionality."

Suggested latent distribution caption:

"Latent norm and PCA visualizations summarize how the learned shape codes are distributed for different latent dimensions. These plots support the quantitative comparison by showing how the representation changes as latent capacity increases."

## Suggested Report Structure

1. Introduction: DeepSDF represents shapes as continuous signed distance functions conditioned on learned latent codes.
2. Reproduction: Explain the local reproduced DeepSDF training and evaluation pipeline.
3. Latent-dimension experiment: Compare 64, 128, and 256 dimensions under the same class/checkpoint setup.
4. Quantitative results: Present the table above, emphasizing the 64-to-256 improvement.
5. Qualitative results: Use airplane reconstruction and interpolation figures.
6. Latent distribution analysis: Use norm/PCA figures to discuss representation structure.
7. Limitations: Chair is a quick subset; full official chair evaluation is optional future polish.
8. Conclusion: The reproduction is successful enough to show the expected trend that larger latent code capacity improves reconstruction.

## Final Checklist Before Submission

- State clearly that airplane and lamp are full official test splits.
- State clearly that chair is a quick 128-shape subset.
- Use test-time optimized MAE as the main comparison.
- Include at least one qualitative reconstruction figure.
- Include one latent distribution or interpolation figure.
- Avoid claiming the chair quick subset is the full chair benchmark.

