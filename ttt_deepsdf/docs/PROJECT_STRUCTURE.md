# Project Structure

This folder is organized as a self-contained research artifact package for
DeepSDF reproduction, DeepSDF-family test-time adaptation, and future baseline
comparisons.

```text
ttt_deepsdf/
  baselines/
    BASELINE_REGISTRY.json # status map for all baseline families
    deepsdf_reference/      # small DeepSDF reference code/configs
    curriculum_deepsdf/     # Curriculum DeepSDF code and pending-result docs
    sota_context/           # external baseline staging docs/scripts/envs
  scripts/                  # TTT evaluation and reconstruction scripts
  results/
    tables/                 # main DeepSDF-vs-TTT result tables
    source_jsons/           # sanitized machine-readable run summaries
    selected_cases/         # selected-case manifests
    deepsdf_latent/         # DeepSDF latent-dimension reproduction results
    deepsdf_planes_600epoch/# original airplane DeepSDF reproduction note
  figures/
    deepsdf_latent/         # DeepSDF latent figures
    deepsdf_planes_600epoch/# original airplane DeepSDF visualization figures
    ...                     # TTT qualitative and summary figures
  docs/                     # reproduction, data, and result notes
  configs/                  # example TTT configs
```

Large datasets, checkpoints, full reconstructed meshes, and third-party cloned
baseline repositories should be placed in `external_artifacts/` after download.
They are intentionally ignored by Git.




