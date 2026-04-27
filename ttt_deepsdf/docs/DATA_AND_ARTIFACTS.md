# Data And Artifact Policy

This repository stores only small files needed to understand and rerun the experiments. Large files are hosted separately on Google Drive and should be unpacked into `ttt_deepsdf/external_artifacts/` or another local workspace when reproducing.

## Two Google Drive Folders

There are two external folders. Keep their roles separate:

| Folder | Use this for | Link |
| --- | --- | --- |
| Processed dataset folder | Airplane/chair/lamp DeepSDF-ready data: SDF samples, normalization parameters, official-style splits, and surface samples used for Chamfer/evaluation. | https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=sharing |
| Result/model artifact folder | Model checkpoints, reconstructed meshes, cloud/server snapshots, result archives, report snapshots, and provenance packages. | https://drive.google.com/drive/folders/1EPH4qcBP8OfL0nSVdleFuJZi2a7E6H4a?usp=sharing |

If you only want to read the report and inspect summarized metrics, cloning this GitHub repository is enough. If you want to rerun evaluation, download the processed dataset folder first. If you want to audit or reuse the exact trained outputs, download the result/model artifact folder as well.

## What Is In Git

- DeepSDF, TTT, LoRA, LoRA-FA, and Curriculum-DeepSDF helper code.
- Result CSV tables and compact JSON summaries.
- Selected qualitative figures and communication figures.
- Reproduction notes, baseline notes, report-facing documentation, and artifact manifests.

## What Stays Out Of Git

- ShapeNet raw data.
- Processed DeepSDF `.npz` SDF samples and full surface samples.
- Full model checkpoints and latent-code checkpoints.
- Full reconstructed mesh folders.
- Per-shape `TTTStates/*.pth`.
- Full cloud server snapshots and local experiment archives.

## Recommended External Packages

| Package | Expected folder | Approx. size | Required? | Purpose |
| --- | --- | ---: | --- | --- |
| `deepsdf_processed_data_airplane_chair_lamp_20260427.tar` | Processed dataset folder | about 55 GiB | Required for rerun/evaluation | Processed SDF samples, normalization parameters, and surface samples for airplane, chair, and lamp. |
| `final_live_results_30446_latest.tar` | Result/model artifact folder | 6.66 GiB | Optional provenance | Verified full 30446 cloud result snapshot. |
| `final_live_results_30622_latest.tar` | Result/model artifact folder | 7.73 GiB | Optional provenance | Final 30622 cloud result snapshot. |
| `final_chair_e200_30446_latest.tar` | Result/model artifact folder | 2.47 GiB | Optional targeted backup | Repaired chair CurriculumDeepSDF-fullish checkpoint-200 archive. Redundant with the full 30446 package but convenient. |
| `completed_baselines_30446_latest.tar` | Result/model artifact folder | 1.05 GiB | Optional legacy snapshot | Earlier completed-baseline snapshot from 30446. |
| `completed_baselines_30622_latest.tar` | Result/model artifact folder | 0.94 GiB | Optional legacy snapshot | Earlier completed-baseline snapshot from 30622. |
| `deepsdf_repo_reports_snapshot_20260427.tar` | Result/model artifact folder | small | Recommended | Repo/report/document snapshot for offline handoff. |

Local upload staging path used by the project owner:

```text
E:\DeepSDF_GDrive_Upload_20260427
```

The staging folder is not part of Git. It is a local upload target for Google Drive web upload.

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
- Recompute tables from processed samples: download the processed dataset folder.
- Inspect exact cloud outputs/checkpoints/meshes: download the result/model artifact folder.
- Verify the late chair e200 repair only: download `final_chair_e200_30446_latest.tar` from the result/model artifact folder.

## Path Hygiene

Committed result files use relative or sanitized paths. Local desktop paths, SSH endpoints, and server-internal paths are documented only in private handoff notes, not required for public reproduction.