# Baselines

This directory separates matched DeepSDF-family baselines from external SOTA
context baselines.

## Included Now

- `deepsdf_reference/`: small DeepSDF code/config reference.
- `curriculum_deepsdf/`: Curriculum DeepSDF code and reproduction notes.
- `sota_context/`: staging docs, scripts, and environments for ConvONet,
  Occupancy Networks, NKSR, and POCO.
- `BASELINE_REGISTRY.json`: compact machine-readable status map.

## Result Policy

The current committed results focus on reproduced DeepSDF and TTT comparisons.
Curriculum DeepSDF and external SOTA baseline result tables are intentionally
marked pending until their runs are finished and checked under a fair protocol.

Large third-party repositories, checkpoints, meshes, and raw run outputs should
be placed under `ttt_deepsdf/external_artifacts/baselines/` after download.

