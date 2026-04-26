# SOTA Baseline Deployment Plan

Updated: 2026-04-25, Asia/Singapore

Purpose: choose deployable and fair comparison baselines for the DeepSDF
parameter-efficient test-time adaptation paper direction.

## Current Position

The strongest paper claim should remain:

> Parameter-efficient test-time decoder adaptation improves the standard
> DeepSDF test-time latent optimization baseline under matched checkpoint,
> split, observations, and evaluation.

This is not yet a global SOTA claim. External SOTA methods often solve a
different problem: reconstructing a surface from point clouds, voxels, images,
or partial observations. They can be useful comparison/context baselines only
if the input protocol is stated clearly.

## Baseline Tiers

### P0: Must Run, Fair And Fast

These use the existing DeepSDF/TTT pipeline and are the most defensible.

| Baseline | Why | Status / Action |
| --- | --- | --- |
| DeepSDF latent-only `test_opt` full split | Direct official-style baseline | Running now for checkpoint 100 full Chamfer |
| DeepSDF latent-only best-of-2 or best-of-N | DeepSDF paper notes stochastic reconstruction and best-of-2 can matter | Add after full Chamfer if time permits |
| DeepSDF latent-only matched wall-clock | Tests whether LoRA only wins because it spends more compute | Reuse same evaluator, raise latent iterations until time matches LoRA |
| Last-layer / decoder-head fine-tune | Tests whether any decoder adaptation works, not just LoRA | Implement as a heavier adaptation baseline |
| Full decoder fine-tune, small subset first | Upper-cost reference; likely overfits but useful reviewer control | Run selected subset only unless promising |

Recommended first new run after current full Chamfer:

1. `latent_only_i500` on lamp and airplane, checkpoint 100.
2. `latent_only_best2_i200` on lamp, then airplane/chair if cheap.
3. `last_layer_ttt_i100` on lamp.

### P1: External Baselines Worth Deploying

These are useful for a "toward SOTA" context table, but must be marked as
different input protocol unless we reproduce exactly matched inputs.

| Method | Type | Why Include | Deployment Risk |
| --- | --- | --- | --- |
| Convolutional Occupancy Networks | point cloud / voxel implicit reconstruction | Public code, ShapeNet pretrained models, standard mesh evaluation | Medium; old deps but official configs/checkpoints exist |
| Occupancy Networks | occupancy implicit baseline | Classic predecessor with public pretrained pointcloud/voxel configs | Medium; older deps, but useful citation/context |
| NKSR | neural point-cloud surface reconstruction | CVPR 2023, strong modern surface reconstruction, public code, pretrained-style usage | Medium-high; CUDA build and normals/data conversion needed |
| POCO | point-cloud surface reconstruction | CVPR 2022, direct point-cloud surface baseline | Medium-high; code/data path work needed |

Recommended external deployment order:

1. ConvONet pointcloud pretrained inference on lamp first.
2. NKSR inference on our sampled surface point clouds for lamp first.
3. If both work, repeat on airplane/chair.
4. POCO only if NKSR/ConvONet comparison is insufficient.

### P2: Cite Or Investigate, Not Immediate

| Method | Reason |
| --- | --- |
| IF-Net | Public code but demands large preprocessed ShapeNet data and old CUDA-style setup; likely too heavy for tonight |
| NoKSR | Very relevant 2025 SOTA-style surface reconstruction, but code/pretrained maturity must be checked before relying on it |
| DeepLS / LDIF / AtlasNet | Useful related work, but less deployment-efficient for our immediate paper story |
| SDFusion / 3DShape2VecSet / diffusion shape models | Generation/completion context, not a direct matched reconstruction baseline |

## Fairness Rules

For internal DeepSDF baselines:

- Same checkpoint.
- Same official test split.
- Same SDF/surface observations.
- Same evaluation script and Chamfer scaling.
- Report runtime and trainable parameters.

For external point-cloud baselines:

- Generate the input point cloud from the same test shapes.
- Report point count and whether normals are used.
- Do not claim identical supervision to DeepSDF/TTT.
- Use our evaluator on their output meshes where possible.
- Put results in a separate "external context" table, not the main matched table.

## Concrete Deployment Plan

### Stage A: While Current GPU Jobs Run

- Do not start new GPU experiments.
- Prepare baseline repository folders under server workspace only.
- Check install feasibility and dependency conflicts.
- Prepare conversion scripts from our SurfaceSamples / meshes to point clouds.

### Stage B: First Free GPU

Run internal stronger DeepSDF controls:

1. lamp `latent_only_i500`.
2. lamp `latent_only_best2_i200`.
3. lamp `last_layer_ttt_i100`.

If these are clean, run airplane and chair.

### Stage C: External Context Baselines

1. Deploy ConvONet in an isolated conda environment.
2. Run one lamp smoke test with official/pretrained pointcloud config.
3. Export meshes and evaluate with our Chamfer evaluator.
4. Deploy NKSR in a separate conda environment.
5. Run lamp smoke test from our surface point clouds with normals.

## Suggested Paper Framing

Main result:

> Our method improves DeepSDF's official-style latent optimization under a
> matched test-time adaptation protocol.

External-context result:

> Modern point-cloud surface methods such as ConvONet/NKSR solve a neighboring
> problem with different observations. We include them as context, while keeping
> DeepSDF latent optimization as the direct baseline.

## Primary Sources Checked

- DeepSDF official repo: https://github.com/facebookresearch/DeepSDF
- Occupancy Networks official repo: https://github.com/autonomousvision/occupancy_networks
- Convolutional Occupancy Networks official repo: https://github.com/autonomousvision/convolutional_occupancy_networks
- IF-Net official repo: https://github.com/jchibane/if-net
- NKSR official repo: https://github.com/nv-tlabs/nksr
- POCO official repo: https://github.com/valeoai/POCO
- NoKSR project/code: https://theialab.github.io/noksr/ and https://github.com/theialab/noksr



