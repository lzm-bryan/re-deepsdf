# Baseline Selection And Fairness

Updated: 2026-04-25, Asia/Singapore

## Recommended Main Claim

Use DeepSDF latent-only `test_opt` as the direct baseline and compare against
parameter-efficient test-time adaptation under matched data, checkpoint,
split, and evaluator.

Do not claim global SOTA until full-class Chamfer/EMD or a protocol-aligned
external benchmark is complete.

## Direct Baselines

| Baseline | Role | Why It Matters |
| --- | --- | --- |
| DeepSDF `test_opt` | Primary baseline | Same model family and same inference setting |
| Latent-only high-iteration | Compute-control baseline | Tests whether LoRA only wins from more optimization |
| Latent-only best-of-2 | Stochastic-control baseline | DeepSDF-style recon can vary by initialization |
| Last-layer TTT | Adaptation-control baseline | Tests whether LoRA is better than a simple decoder-head update |
| Full decoder TTT | Upper-cost baseline | Shows quality/cost tradeoff against unrestricted adaptation |

## External Context Baselines

| Method | Input Type | Use In Paper |
| --- | --- | --- |
| ConvONet | point cloud or voxel features | Context table if we can run pretrained/config-compatible inference |
| Occupancy Networks | point cloud / voxel / image variants | Classic implicit baseline context |
| NKSR | point cloud with normals | Modern surface reconstruction context |
| POCO | point cloud | Modern point-cloud surface baseline context |

## Fairness Rules

For DeepSDF-family controls:

- Same checkpoint.
- Same official split.
- Same SDF/surface observations.
- Same evaluator and Chamfer scale.
- Report runtime, iteration count, trainable parameters, and memory.

For external methods:

- State input modality and point count.
- State whether normals are used.
- Evaluate generated meshes with the same local evaluator when possible.
- Keep external numbers out of the main matched table unless protocol is
  truly aligned.

## First Experiments After Current Queue

1. Lamp latent-only high-iteration (`i500`).
2. Lamp latent-only best-of-2 (`i200` each).
3. Lamp last-layer TTT (`i100`).
4. Repeat on airplane and chair if the lamp controls are informative.




