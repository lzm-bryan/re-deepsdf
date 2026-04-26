# External Baseline Context

This folder contains small staging files for future external baseline
comparisons. It intentionally does not vendor complete third-party repositories
or checkpoints.

## Included

- `docs/`: baseline selection, fairness, and deployment notes.
- `envs/`: environment YAML files for candidate methods.
- `scripts/`: staging and manifest-generation helpers.
- `data_manifests/manifest.json`: compact manifest summary.

## Candidate Baselines

- Convolutional Occupancy Networks.
- Occupancy Networks.
- NKSR.
- POCO.

These methods use different inputs and assumptions. Keep them as context
baselines unless the protocol is carefully aligned with the DeepSDF/TTT setup.

Full third-party repositories, model weights, and generated outputs belong in:

```text
ttt_deepsdf/external_artifacts/baselines/sota_context/
```




