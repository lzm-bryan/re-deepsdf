# SOTA Baseline Guide

This package includes staging code and documentation for future SOTA context
baselines, but it does not commit their complete repositories or results.

## Why These Are Separate

The main claim is a matched DeepSDF-family comparison: same data, same split,
same checkpoints, and the same evaluator. External baselines such as ConvONet,
Occupancy Networks, NKSR, and POCO often use different inputs and assumptions.
They should be treated as context unless their protocol is aligned carefully.

## Candidate Methods

| Method | Input Style | Included Material | Result Status |
| --- | --- | --- | --- |
| ConvONet | point cloud or voxel features | env + staging docs | pending |
| Occupancy Networks | point cloud / voxel / image variants | staging docs | pending |
| NKSR | point cloud with normals | env + staging docs | pending |
| POCO | point cloud | env + staging docs | pending |

## Code Locations

- Baseline registry: `baselines/BASELINE_REGISTRY.json`
- Environment files: `baselines/sota_context/envs/`
- Staging scripts: `baselines/sota_context/scripts/`
- Fairness notes: `baselines/sota_context/docs/BASELINE_SELECTION_AND_FAIRNESS.md`

## Recommended Next Step

After the Google Drive artifacts are finalized, place external baseline clones
and outputs under:

```text
ttt_deepsdf/external_artifacts/baselines/sota_context/
```

Then add only compact, checked summary tables back into Git.

