# DeepSDF Reference Baseline

This directory contains a small copy of the DeepSDF reference code and configs
needed by the TTT scripts in this artifact package.

## Contents

- `source_code/src/`: DeepSDF Python modules and training/evaluation scripts.
- `source_code/networks/`: decoder architecture.
- `configs/`: example model specs for the reproduced runs.
- `docs/`: original repository-level notes kept for context.

## Role In The Experiments

DeepSDF latent-only test-time optimization is the primary matched baseline.
The TTT methods reuse the same decoder checkpoints, splits, and SDF samples,
then add residual, LoRA, or LoRA-FA adaptation during inference.

Full checkpoints and data are external artifacts. They are not committed here.




