# Google Drive Artifact Manifest - 2026-04-27

This document records the large artifacts that should live outside GitHub. It is intended for readers who want to reuse the prepared data/results instead of recomputing them.

## External Folders

| Folder | Role | Link |
| --- | --- | --- |
| Processed dataset folder | Three-class airplane/chair/lamp processed data, including train/test SDF, normalization parameters, split files, and surface samples. | https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=sharing |
| Result/model artifact folder | Model checkpoints, reconstructed meshes, server snapshots, result archives, and report/source snapshots. | https://drive.google.com/drive/folders/1EPH4qcBP8OfL0nSVdleFuJZi2a7E6H4a?usp=sharing |

## Packages Prepared By The Project Owner

| File name | Folder | Size | Contents | Upload priority |
| --- | --- | ---: | --- | --- |
| `deepsdf_processed_data_airplane_chair_lamp_20260427.tar` | Processed dataset folder | about 55 GiB | Processed DeepSDF data for airplane/chair/lamp, including SDF, normalization, and surface samples. | High |
| `final_live_results_30446_latest.tar` | Result/model artifact folder | 6.66 GiB | Full verified 30446 result snapshot; includes logs, summaries, checkpoints, meshes, and TTTStates. | High |
| `final_live_results_30622_latest.tar` | Result/model artifact folder | 7.73 GiB | Full 30622 result snapshot. | High |
| `final_chair_e200_30446_latest.tar` | Result/model artifact folder | 2.47 GiB | Targeted repaired chair fullish e200 result package. | Medium |
| `completed_baselines_30446_latest.tar` | Result/model artifact folder | 1.05 GiB | Earlier 30446 baseline archive. | Low |
| `completed_baselines_30622_latest.tar` | Result/model artifact folder | 0.94 GiB | Earlier 30622 baseline archive. | Low |
| `deepsdf_repo_reports_snapshot_20260427.tar` | Result/model artifact folder | small | Small source/report/handoff snapshot. | High |

## Local Staging Path

```text
E:\DeepSDF_GDrive_Upload_20260427
```

The staging folder is not part of Git. It is a local upload target for Google Drive web upload.

## Notes For Reusers

The main paper/report claim does not require downloading every archive. The GitHub repository already contains compact tables and figures. Download the processed dataset folder only when rerunning experiments; download the result/model artifact folder when auditing checkpoints, meshes, or exact cloud outputs.