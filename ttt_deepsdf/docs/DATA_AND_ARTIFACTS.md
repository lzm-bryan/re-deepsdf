# Data And Artifact Policy

This repository stores only small files needed to understand and rerun the experiments. Large files are hosted separately, for example on Google Drive, and should be unpacked into `ttt_deepsdf/external_artifacts/` or another local workspace when reproducing.

## Google Drive Folder

Owner-managed artifact folder:

<https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=sharing>

If you only want to read the report and inspect the summarized metrics, cloning this GitHub repository is enough. If you want to rerun evaluation or reuse the exact reconstructed meshes/checkpoints, download the external artifacts listed below.

## What Is In Git

- TTT / LoRA source code and small helper scripts.
- Result CSV tables and compact JSON summaries.
- Selected qualitative figures and communication figures.
- Reproduction notes, baseline notes, and report-facing documentation.

## What Stays Out Of Git

- ShapeNet raw data.
- Processed DeepSDF `.npz` SDF samples and full surface samples.
- Full model checkpoints and latent-code checkpoints.
- Full reconstructed mesh folders.
- Per-shape `TTTStates/*.pth`.
- Full cloud server snapshots and local experiment archives.

## Recommended Drive Packages

| Package | Approx. size | Required? | Purpose |
| --- | ---: | --- | --- |
| `deepsdf_processed_data_airplane_chair_lamp_20260427.tar` | about 55 GiB | Required for rerun/evaluation | Processed SDF samples, normalization parameters, and surface samples for airplane, chair, and lamp. |
| `final_live_results_30446_latest.tar` | 6.66 GiB | Optional provenance | Verified full 30446 cloud result snapshot. |
| `final_live_results_30622_latest.tar` | 7.73 GiB | Optional provenance | Final 30622 cloud result snapshot. |
| `final_chair_e200_30446_latest.tar` | 2.47 GiB | Optional targeted backup | Repaired chair CurriculumDeepSDF-fullish checkpoint-200 archive. Redundant with the full 30446 package but convenient. |
| `completed_baselines_30446_latest.tar` | 1.05 GiB | Optional legacy snapshot | Earlier completed-baseline snapshot from 30446. |
| `completed_baselines_30622_latest.tar` | 0.94 GiB | Optional legacy snapshot | Earlier completed-baseline snapshot from 30622. |
| `deepsdf_repo_reports_snapshot_20260427.tar` | small | Recommended | Repo/report/document snapshot for offline handoff. |

Local upload staging path used by the project owner:

```text
E:\DeepSDF_GDrive_Upload_20260427
```

The staging folder contains `README_UPLOAD_FIRST.md` and `UPLOAD_MANIFEST_2026-04-27.csv`, plus any packages that have finished building/copying.

## Expected External Layout After Download

For rerunning the main DeepSDF/TTT commands, extract the processed-data tar and arrange it as:

```text
external_artifacts/
  data/
    SdfSamples/ShapeNetV2/02691156/*.npz
    SdfSamples/ShapeNetV2/03001627/*.npz
    SdfSamples/ShapeNetV2/03636649/*.npz
    NormalizationParameters/ShapeNetV2/<class_id>/*
    SurfaceSamples/ShapeNetV2/<class_id>/*
  splits/
    sv2_planes_train.json
    sv2_planes_test.json
    sv2_chairs_train.json
    sv2_chairs_test.json
    sv2_lamps_train.json
    sv2_lamps_test.json
```

The local processed data used in the final experiments had these counts:

| Class | Train split | Test split | SDF/Norm files | Surface files |
| --- | ---: | ---: | ---: | ---: |
| airplane `02691156` | 1780 | 456 | 2236 | 456 |
| chair `03001627` | 3281 | 832 | 4113 | 832 |
| lamp `03636649` | 897 | 213 | 1110 | 213 |

## How To Choose What To Download

- Read-only report inspection: clone GitHub only.
- Recompute tables from processed samples: download `deepsdf_processed_data_airplane_chair_lamp_20260427.tar`.
- Inspect exact cloud outputs/checkpoints/meshes: download the two `final_live_results_*` archives.
- Verify the late chair e200 repair only: download `final_chair_e200_30446_latest.tar`.

## Path Hygiene

Committed result files use relative or sanitized paths. Local desktop paths, SSH endpoints, and server-internal paths are documented only in private handoff notes, not required for public reproduction.