# TTT Scripts

These scripts expect an existing DeepSDF experiment directory with this layout:

```text
experiment_name/
  specs.json
  ModelParameters/<checkpoint>.pth
  LatentCodes/<checkpoint>.pth
```

The `--deepsdf-dir` argument should point to a directory that exposes the
DeepSDF `deep_sdf` package and `networks` package. In this repository that is
usually:

```text
source_code/src
```

## Scripts

- `evaluate_sdf_latent_opt.py`: baseline test-time latent optimization.
- `evaluate_sdf_ttt.py`: residual, LoRA, and LoRA-FA SDF-MAE evaluation.
- `reconstruct_ttt_adapted_meshes.py`: adapted mesh generation plus Chamfer
  evaluation against surface samples.

Use `--surface-root` when surface samples live outside `--data-root`.




