# Curriculum DeepSDF Baseline

This folder stores the small code/config pieces for the Curriculum DeepSDF
baseline direction. The large checkpoints, meshes, and run folders are not
committed to Git.

## Included

- `scripts/make_curriculum_fullish_specs.py`
- `scripts/make_curriculum_fullish_train.py`
- `scripts/train_deep_sdf_curriculum_fullish.generated.py`
- `configs/lamp_curriculum_fullish_e100_specs.json`

## Current Status

Curriculum DeepSDF is kept as a baseline direction, but its report-facing
baseline results are not part of the main DeepSDF-vs-TTT claim yet. Treat its
current outputs as pending or external unless a matching result table is added
later.

## Reproduction Outline

1. Download the external DeepSDF data/checkpoint artifacts.
2. Generate or edit a curriculum spec with `make_curriculum_fullish_specs.py`.
3. Use `train_deep_sdf_curriculum_fullish.generated.py` to run the curriculum
   training schedule.
4. Evaluate with the same SDF-MAE and Chamfer scripts used for the main
   DeepSDF/TTT comparisons.

Large output directories should be placed under:

```text
ttt_deepsdf/external_artifacts/baselines/curriculum_deepsdf/
```




