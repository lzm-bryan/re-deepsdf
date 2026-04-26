# Data And Artifact Policy

This repository stores only small files needed to understand and rerun the
experiments. Large files should be hosted separately, for example on Google
Drive, and unpacked into `ttt_deepsdf/external_artifacts/` when reproducing.

## Put In Git

- TTT source code.
- Result CSV tables.
- Small JSON summaries.
- Selected-case manifests.
- PNG/SVG figures used by the report.
- Documentation and example commands.

## Keep Out Of Git

- ShapeNet raw data.
- Processed DeepSDF `.npz` data.
- Full model checkpoints and latent-code checkpoints.
- Full reconstructed mesh folders.
- Per-shape `TTTStates/*.pth`.
- Full server snapshots and local experiment archives.

## Expected External Layout

After downloading external artifacts, arrange them like this:

```text
ttt_deepsdf/external_artifacts/
  data/
    SdfSamples/ShapeNetV2/<class_id>/*.npz
    NormalizationParameters/ShapeNetV2/<class_id>/*.npz
  surface_data/
    SurfaceSamples/ShapeNetV2/<class_id>/*.ply
  splits/
    sv2_planes_test.json
    sv2_chairs_test.json
    sv2_lamps_test.json
  experiments/
    airplane_code256_e100/
    airplane_code256_e200/
    chair_code256_e100/
    chair_code256_e200/
    lamp_code256_e100/
    lamp_code256_e200/
  server_snapshots/
    30446/
    30622/
  local_experiments/
    paper_ckpt200_full_chamfer_local/
```

Only `data/`, `surface_data/`, `splits/`, and `experiments/` are required to
rerun the main commands. The `server_snapshots/` and `local_experiments/`
folders are optional provenance archives referenced by sanitized result tables.

## Data Link Placeholder

Google Drive folder for external data/artifacts:

```text
https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=drive_link
TODO: Optional SHA256 checksum or file-size note.
```

If the result mesh/checkpoint archive is uploaded separately, add it here:

```text
TODO: Google Drive link for checkpoints, reconstructed meshes, and TTT states.
```

## Privacy And Path Hygiene

The committed result files use relative paths such as
`external_artifacts/server_snapshots/...`. They intentionally avoid local user
names, desktop paths, machine names, SSH endpoints, and internal server roots.



