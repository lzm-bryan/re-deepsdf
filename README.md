# DeepSDF 复现与 TTT/LoRA 扩展实验

[中文](README.md) | [English](README.en.md)

这个仓库整理了两部分工作：

1. 基础 DeepSDF 复现：最早的飞机类 600 epoch 复现实验、数据处理记录、推理/可视化脚本。
2. TTT/LoRA 扩展实验：在 DeepSDF 测试时 latent 优化的基础上，加入 residual TTT、LoRA-TTT、LoRA-FA 等轻量自适应模块，并整理三类 ShapeNet 数据集上的结果。

仓库本身只保存适合 GitHub 的小文件：代码、配置、结果表、精选图片和复现文档。完整数据、checkpoint、mesh、server snapshot 等大文件放在 Google Drive 中。

## 入口导航

| 目标 | 建议入口 | 说明 |
| --- | --- | --- |
| 跑通基础 DeepSDF 飞机复现 | [README.en.md](README.en.md) 或本 README 下方说明 | 包含基础环境、数据、推理、训练和评估说明。 |
| 查看 TTT/LoRA 改进实验 | [ttt_deepsdf/README.zh-CN.md](ttt_deepsdf/README.zh-CN.md) | 三类数据集、DeepSDF baseline、TTT/LoRA/LoRA-FA、Curriculum DeepSDF 和 SOTA/context baseline 文档。 |
| 查看大文件如何获取 | [ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md](ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md) | 说明哪些文件不进 GitHub、哪些应该从 Google Drive 下载。 |
| 查看 Google Drive 上传/下载清单 | [ttt_deepsdf/docs/GOOGLE_DRIVE_ARTIFACT_MANIFEST_2026-04-27.md](ttt_deepsdf/docs/GOOGLE_DRIVE_ARTIFACT_MANIFEST_2026-04-27.md) | 给出 processed data、server result archives、repo/report snapshot 的文件名和用途。 |
| 追溯历史数据处理过程 | [数据处理复现/](数据处理复现/) | 保留早期数据处理、服务器复现、参考材料记录。一般读者可以先跳过。 |

## 当前主要结论

在已完成的 airplane、chair、lamp 三类 ShapeNet split 上，LoRA 测试时自适应在 matched DeepSDF 设置下，比复现的 latent-only DeepSDF baseline 有更低的 SDF-MAE 和 full-split Chamfer。这个结论是课程/项目级的受控比较，不宣称严格外部 SOTA。

详细数值见：

- [ttt_deepsdf/docs/RESULTS_SUMMARY.md](ttt_deepsdf/docs/RESULTS_SUMMARY.md)
- [ttt_deepsdf/results/tables/ttt_sdf_mae_summary.csv](ttt_deepsdf/results/tables/ttt_sdf_mae_summary.csv)
- [ttt_deepsdf/results/tables/full_chamfer_summary.csv](ttt_deepsdf/results/tables/full_chamfer_summary.csv)

## 大文件与 Google Drive

Google Drive artifact 文件夹：

<https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=sharing>

如果只想阅读报告、看结果表和小图，clone GitHub 即可。如果想直接复用我已经处理好的数据和云端实验结果，请下载 Google Drive 中的 artifact：

| 文件 | 用途 |
| --- | --- |
| `deepsdf_processed_data_airplane_chair_lamp_20260427.tar` | 三类完整 processed data：SDF、NormalizationParameters、SurfaceSamples。 |
| `final_live_results_30446_latest.tar` | 30446 服务器完整结果快照。 |
| `final_live_results_30622_latest.tar` | 30622 服务器完整结果快照。 |
| `final_chair_e200_30446_latest.tar` | 修复后的 chair CurriculumDeepSDF-fullish e200 定向备份。 |
| `deepsdf_repo_reports_snapshot_20260427.tar` | 小型文档/报告/repo 快照，便于离线交接。 |

更完整说明见 [DATA_AND_ARTIFACTS.md](ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md)。

## 仓库结构

```text
re-deepsdf/
├── configs/                # 基础 DeepSDF 飞机实验配置
├── generated/              # 小型生成 mesh 示例
├── images/                 # 基础复现实验图片
├── models/                 # 小型模型/latent 示例，不包含全量 checkpoint
├── scripts/                # 基础生成、渲染、可视化脚本
├── source_code/            # DeepSDF 训练、重建、评估代码
├── ttt_deepsdf/            # TTT/LoRA DeepSDF 研究包
└── 数据处理复现/           # 历史数据处理与复现记录
```

## 快速开始

```bash
git clone https://github.com/lzm-bryan/re-deepsdf.git
cd re-deepsdf

# 基础飞机类生成示例
python scripts/generate_new_planes.py -n 5
python scripts/visualize_compare.py single generated/GeneratedPlanes/generated_plane_001.ply
```

如果要运行 TTT/LoRA 三类实验，请先阅读：

```text
ttt_deepsdf/README.zh-CN.md
ttt_deepsdf/docs/REPRODUCTION_GUIDE.md
ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md
```

## 说明

- GitHub 仓库不保存 ShapeNet raw data、完整 processed data、全量 checkpoint、全量 mesh 或逐样本 TTTStates。
- 外部 artifact 上传后，建议保持 manifest 中的文件名不变，方便其他人按文档下载。
- 当前结果主要用于课程作业、论文雏形和后续扩展实验；如果要写严格论文，需要进一步补充更长训练预算和同协议外部 baseline。