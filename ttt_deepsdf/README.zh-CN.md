# TTT-DeepSDF 结果与复现包

[中文](README.zh-CN.md) | [English](README.md)

这个目录保存 DeepSDF 测试时自适应实验中适合放入 Git 的小型材料，包括 TTT 评估代码、整理后的结果表、定性可视化图片和复现说明。

大体量数据、完整 checkpoint、重建 mesh 以及每个 shape 的 TTT 中间状态不直接放在 Git 里。需要复现时，请先按 `docs/DATA_AND_ARTIFACTS.md` 下载外部文件，并解压到 `external_artifacts/`。

## 包含内容

- `scripts/`：可复用的 TTT 评估和 mesh 重建脚本。
- `baselines/`：DeepSDF 参考代码、Curriculum DeepSDF 代码，以及外部 baseline 的占位说明和准备脚本。
- `results/tables/`：用于论文或报告的小型 CSV 汇总表。
- `results/deepsdf_latent/`：DeepSDF latent 维度复现实验结果。
- `results/deepsdf_planes_600epoch/`：原始飞机类 DeepSDF 复现实验产物说明。
- `results/source_jsons/`：清理过的、机器可读的运行摘要。
- `results/selected_cases/`：精选 case 的 CSV/JSON 清单。
- `figures/`：小型定性图和汇总图。
- `docs/`：复现指南、外部 artifact 策略和结果总结。
- `configs/`：示例命令配置。

## 建议阅读顺序

如果只想快速了解这个目录：

1. 先看 `docs/RESULTS_SUMMARY.md`，了解 DeepSDF 与 TTT 的主要对比结论。
2. 再看 `docs/REPRODUCTION_GUIDE.md`，里面整理了可运行命令。
3. 如果想理解目录组织方式，看 `docs/PROJECT_STRUCTURE.md`。
4. 如果关注 Curriculum DeepSDF 或其他 SOTA baseline，看 `baselines/README.md` 和 `docs/SOTA_BASELINE_GUIDE.md`。

本目录中的文件刻意保持较小。完整数据集、checkpoint、mesh 和逐样本 TTT 状态都作为外部 artifact 管理。

## 当前主要结果

在已经完成的飞机、椅子、台灯三类 SDF-MAE 和 full-split Chamfer 对比中，LoRA 测试时自适应在 checkpoint 100 和 200 上都优于复现的 DeepSDF baseline。具体数值和结论边界请看 `docs/RESULTS_SUMMARY.md`。

## 快速开始

安装依赖：

```bash
pip install -r ttt_deepsdf/requirements.txt
```

下载外部 artifact 后，运行 LoRA SDF-MAE 评估：

```bash
python ttt_deepsdf/scripts/evaluate_sdf_ttt.py \
  --deepsdf-dir source_code/src \
  --experiment external_artifacts/experiments/airplane_code256_e200 \
  --checkpoint 200 \
  --data-root external_artifacts/data \
  --split-file external_artifacts/splits/sv2_planes_test.json \
  --mode lora \
  --iters 100 \
  --output-subdir EvaluationTTT \
  --output-name lora_summary_200.json
```

完整 mesh 重建和 Chamfer 评估命令见 `docs/REPRODUCTION_GUIDE.md`。

## 外部数据和大文件

三类数据和较大的实验产物放在 Git 之外：

```text
Google Drive folder:
https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=drive_link
```

推荐把下载链接、文件说明和 checksum 统一维护在 `docs/DATA_AND_ARTIFACTS.md`。这个 README 只保留最小入口，避免以后多个地方同时改链接。
