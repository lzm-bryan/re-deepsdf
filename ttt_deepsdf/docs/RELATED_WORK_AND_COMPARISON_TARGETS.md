# Related Work And Comparison Targets

Purpose:

This note translates recent related work into concrete comparison choices for
the current DeepSDF / TTT paper direction. It should be read together with:

- `docs/PAPER_UPGRADE_DIRECTION_GUIDE_2026-04-25.md`
- `docs/PAPER_TTT_METRIC_COMPLETION_PLAN_2026-04-25.md`
- `docs/PAPER_RESULTS_TABLES_2026-04-25.md`

## Paper Position

Working claim:

> Parameter-efficient test-time decoder adaptation improves DeepSDF
> reconstruction over the official-style latent-only `test_opt` inference
> baseline under matched checkpoint, split, observations, and evaluation.

This is not yet a SOTA claim. The current evidence is strong for matched
DeepSDF-style SDF-MAE, and selected-case Chamfer is promising, but full-split
mesh Chamfer is still needed before making strong external-comparison claims.

## Related Work Tiers

| Tier | Methods | Relation to this project | How to use in paper |
| --- | --- | --- | --- |
| Direct baseline | DeepSDF | Same autodecoder family; same test-time latent optimization idea | Primary quantitative baseline |
| Implicit 3D reconstruction | Occupancy Networks, ConvONet, IF-Net, DeepLS, LDIF | Neighboring implicit-surface or local-feature reconstruction methods | Related work and optional context table only if protocol can be matched |
| Surface / point-cloud reconstruction | POCO, NKSR, SAP-style methods | Often SOTA on point-cloud surface reconstruction, but input protocol differs | Related work; avoid direct numeric claims unless using same inputs/metrics |
| Test-time optimization / adaptation | DeepSDF `test_opt`, MetaSDF, TTT | Closest conceptual family: adapt per instance at inference | Use to motivate our latent-plus-adapter inference parameterization |
| Parameter-efficient adaptation | LoRA and adapter-style PEFT | Supplies the low-rank / small-adapter design vocabulary | Use to justify trainable-parameter and runtime reporting |
| Modern generative neural fields | AutoSDF, SDFusion, 3DShape2VecSet and newer diffusion/token methods | Broader neural-field shape modeling, often generation/completion rather than matched reconstruction | Mention as broader context, not primary baseline |

## Common Metrics In Prior Work

| Metric | Used for | Our status | Paper recommendation |
| --- | --- | --- | --- |
| SDF MAE / SDF reconstruction error | Directly measures SDF prediction error on sampled points | Complete for 3 classes, checkpoints 100 and 200 | Keep as main matched DeepSDF/TTT table |
| Chamfer distance | Standard mesh/surface reconstruction metric | Selected 8-case table complete; full split missing | Must run full split for serious paper comparison |
| EMD | Used in DeepSDF-style mesh evaluation but more expensive | Not run | Optional; lower priority than Chamfer |
| IoU | Common for occupancy / voxel-style methods | Not run | Optional only if we can produce watertight occupancy grids consistently |
| Normal consistency | Common in Occupancy/ConvONet-style evaluations | Not run | Optional qualitative/geometry metric if mesh normals are stable |
| F-score | Common in point-cloud/surface reconstruction | Not run | Optional; useful if comparing against POCO/NKSR-style papers |
| Runtime / seconds per shape | Needed for test-time adaptation fairness | Available for several TTT runs | Include in efficiency table |
| Trainable parameters | Needed for PEFT claim | Available for TTT runs | Include in efficiency table |
| GPU memory | Supports practicality claim | Available for newer TTT runs | Include as secondary efficiency field |

## What Can Be Compared Fairly Now

Strong and fair:

- DeepSDF `test_opt` vs residual TTT vs LoRA TTT vs LoRA-FA TTT.
- Same class, same official-style split, same checkpoint, same evaluator.
- Main metric: SDF MAE.
- Current result: LoRA improves over DeepSDF `test_opt` by about 33-50 percent
  across airplane, chair, and lamp in checkpoint 100/200 tables.

Promising but not yet final:

- Selected 8-case Chamfer shows LoRA improvement for all three classes.
- This is useful for qualitative evidence and failure/success case discussion.
- It is not enough for a formal external benchmark table because the subset was
  selected and is not the full test split.

Not fair yet:

- Claiming we beat Occupancy Networks, ConvONet, IF-Net, POCO, NKSR, or other
  external methods using our current SDF-MAE numbers.
- Comparing our selected 8-case Chamfer directly to published full-test
  Chamfer tables.
- Mixing metrics with different scaling conventions, such as raw Chamfer vs
  Chamfer x1000, without verifying normalization and sampling protocol.

## Recommended Comparison Tables

### Table 1: Main Matched DeepSDF Table

Already mostly complete.

Columns:

`Class`, `Checkpoint`, `DeepSDF test_opt`, `Residual TTT`, `LoRA TTT`,
`LoRA-FA TTT`, `Best gain`, `Valid count`.

### Table 2: Full-Split Chamfer

Needed before stronger paper claims.

Rows:

- airplane checkpoint 100: DeepSDF `test_opt` vs LoRA TTT;
- chair checkpoint 100: DeepSDF `test_opt` vs LoRA TTT;
- lamp checkpoint 100: DeepSDF `test_opt` vs LoRA TTT.

Recommended columns:

`Class`, `Method`, `Count`, `Mean Chamfer`, `Median Chamfer`,
`Chamfer x1000`, `Mean gain`, `Median gain`.

### Table 3: Efficiency / PEFT Cost

Rows:

- residual TTT;
- LoRA TTT rank 8;
- LoRA-FA TTT;
- LoRA rank ablations where available.

Columns:

`Method`, `SDF MAE`, `Seconds/shape`, `Trainable params`, `CUDA peak MB`,
`Iterations`.

### Table 4: Ablation

Use lamp first because it is the cheapest full split.

Rows:

- LoRA rank 4 / 8 / 16 at 100 iterations;
- LoRA rank 8 at 25 / 50 / 100 / 200 iterations.

This already has useful checkpoint-100 lamp data.

## Suggested Related-Work Framing

DeepSDF introduced an autodecoder representation where an unseen shape is
reconstructed by optimizing a latent code while keeping the decoder fixed. Our
method keeps this inference setting but changes the test-time parameterization:
instead of adapting only the latent code, we adapt the latent code plus a small
residual or low-rank decoder module.

Occupancy Networks, ConvONet, IF-Net, DeepLS, LDIF, POCO, and NKSR show that
implicit/local/surface reconstruction has become much stronger than the original
global DeepSDF decoder family. However, many of these works use different input
modalities, local encoders, point-cloud assumptions, or evaluation protocols.
They should be discussed as context unless we reproduce a matched protocol.

MetaSDF and general test-time training/adaptation work motivate fast
per-instance adaptation. LoRA and parameter-efficient adaptation motivate why
we report trainable parameters, runtime, and memory instead of only accuracy.

## External Sources To Cite Or Check

Primary and close:

- DeepSDF: https://github.com/facebookresearch/DeepSDF
- Occupancy Networks: https://avg.is.mpg.de/publications/occupancy-networks
- Convolutional Occupancy Networks: https://arxiv.org/abs/2003.04618
- IF-Net: https://virtualhumans.mpi-inf.mpg.de/ifnets/
- DeepLS: https://www.ecva.net/papers/eccv_2020/papers_ECCV/html/6873_ECCV_2020_paper.php
- LDIF: https://arxiv.org/abs/1912.06126
- MetaSDF: https://research.google/pubs/metasdf-meta-learning-signed-distance-functions/

Broader surface / newer context:

- POCO: https://boulch.eu/publications/2022_cvpr_poco/
- NKSR: https://arxiv.org/abs/2305.19590
- 3DShape2VecSet: https://arxiv.org/abs/2301.11445
- SDFusion: https://arxiv.org/abs/2212.04493
- LoRA: https://arxiv.org/abs/2106.09685
- Test-Time Training: https://proceedings.mlr.press/v119/sun20b.html

## Immediate Experiment Decision

For the submission-oriented version, prioritize:

1. Full-split Chamfer for checkpoint 100, baseline vs LoRA, all three classes.
2. Keep SDF-MAE table as the internal matched main result.
3. Use selected 8-case Chamfer and panels as qualitative evidence.
4. Use lamp ablations plus airplane/chair efficiency as the PEFT cost story.
5. Do not claim external SOTA unless a full, protocol-aligned Chamfer table is
   produced and carefully normalized against published metrics.






