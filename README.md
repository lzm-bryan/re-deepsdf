# DeepSDF 飞机重建实验

[中文](README.md) | [English](README.en.md)

本仓库包含一个可复现的 DeepSDF 飞机重建实验、少量生成样例，以及后续
TTT/LoRA 扩展实验。基础实验使用 ShapeNet V2 飞机类别（`02691156`），并提供
训练 600 个 epoch 后的 DeepSDF auto-decoder checkpoint。

## 项目入口

| 目标 | 入口 | 说明 |
| --- | --- | --- |
| 运行基础 DeepSDF 飞机实验 | 本 README | 环境、数据下载、推理、可视化、训练和评估命令。 |
| 追溯数据来源或预处理过程 | [`数据处理复现/`](数据处理复现/README.md) | 历史数据处理说明和外部参考资料；大多数读者可以先跳过。 |
| 阅读 TTT/LoRA 扩展实验 | [`ttt_deepsdf/`](ttt_deepsdf/README.zh-CN.md) | TTT 脚本、结果表、图、复现说明和 baseline 规划文档。 |

建议阅读顺序：先按本 README 跑通基础实验；只有在需要追溯数据来源时再看
`数据处理复现/`；需要查看 TTT/LoRA 研究结果时进入 `ttt_deepsdf/`。

## 仓库结构

```text
re-deepsdf/
|-- configs/              DeepSDF 飞机实验配置
|-- generated/            小型生成 mesh 样例
|-- images/               可视化图片
|-- models/               小型模型参数和 latent code 样例
|-- scripts/              生成、渲染、可视化脚本
|-- source_code/          DeepSDF 训练、重建、评估代码
|-- ttt_deepsdf/          TTT/LoRA DeepSDF 研究包
`-- 数据处理复现/       数据预处理记录和参考资料
```

大体量数据、完整 checkpoint 和全量重建 mesh 不建议直接放入 Git。需要时请从
下方 Google Drive 链接或 `ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md` 下载。

## 快速推理

```bash
git clone https://github.com/lzm-bryan/re-deepsdf.git
cd re-deepsdf

# 如需完整数据，请先从下方链接下载并解压 data/ 目录。

python scripts/generate_new_planes.py -n 5
python scripts/visualize_compare.py single generated/GeneratedPlanes/generated_plane_001.ply
```

## 完整训练复现

如果只查看已提供的模型和生成样例，可以跳过训练。

### 环境

```bash
pip install torch numpy trimesh matplotlib scikit-image open3d
# 或
conda install pytorch numpy trimesh matplotlib scikit-image
```

### 数据准备

下载后解压到仓库根目录的 `data/` 下。

| 数据 | 大小 | 说明 | 链接 |
| --- | ---: | --- | --- |
| 训练数据 | 4.1 GB | 训练用 `SdfSamples` 和 `NormalizationParameters` | [train_4.13planes-600epoch.zip](https://drive.google.com/file/d/1KCqG-tOYm3H92792S17m-JFwLCmFdS0k/view?usp=sharing) |
| 测试数据 | 3.0 GB | 测试用 SDF 采样和归一化参数 | [test_4.13planes-600epoch.zip](https://drive.google.com/file/d/19ENGz3Cnxp_7HmjjBLcPgkSR23UpwqC-/view?usp=sharing) |
| 重建结果 | 261 MB | 456 个重建 mesh | [reconstructions_4.13planes-600epoch.zip](https://drive.google.com/file/d/11KQy6ca7o8MuPxGZBU5PWwAhzOVQhw9n/view?usp=sharing) |
| 隐向量 | 583 KB | 627 个训练样本的 latent code | [latentcodes_4.13planes-600epoch.zip](https://drive.google.com/file/d/1WeusBcG0clPVxzfozuSA0M84I8EKtSN7/view?usp=sharing) |

解压后的推荐结构：

```text
data/
|-- SdfSamples/ShapeNetV2/02691156/
|-- NormalizationParameters/ShapeNetV2/02691156/
|-- TestData/SdfSamples/ShapeNetV2/02691156/
`-- TestData/NormalizationParameters/ShapeNetV2/02691156/
```

### 可选：从 ShapeNet 原始数据生成

1. 在 <https://shapenet.org/> 注册并下载 ShapeNet V2。
2. 下载飞机类别 `02691156`。
3. 生成 DeepSDF 采样数据：

```bash
python source_code/src/generate_training_meshes.py \
    --data-source /path/to/shapenet \
    --shape-category 02691156 \
    --output-dir ./data/SdfSamples
```

### 配置

`configs/specs.json` 提供了飞机实验的默认相对路径配置。

### 训练

```bash
python source_code/src/train_deep_sdf.py \
    --experiment-name planes_600epoch \
    --data-path ./data \
    --epochs 600
```

### 评估

```bash
python source_code/src/reconstruct.py \
    --experiment-name planes_600epoch \
    --checkpoint models/ModelParameters/600.pth

python source_code/src/evaluate.py \
    --experiment-name planes_600epoch \
    --reconstruction-dir ./data/Reconstructions
```

## 数据格式

每个 `.npz` SDF 样本包含：

- `pos`：正采样点，形状为 `N x 4`，格式为 `[x, y, z, sdf]`
- `neg`：负采样点，形状为 `M x 4`，格式为 `[x, y, z, sdf]`

## 模型概览

网络是 DeepSDF auto-decoder：

```python
Decoder(
    latent_size=256,
    dims=[512 x 8],
    latent_in=[4],
    dropout=[0-7],
    weight_norm=True,
)
```

训练策略：

| 参数 | 值 |
| --- | ---: |
| Batch size | 4 scenes |
| Samples per scene | 16384 |
| 初始学习率 | 0.0005 |
| 学习率调度 | Step，每 500 epoch 减半 |
| Code regularization | 1e-4 |

DeepSDF 是 auto-decoder：每个训练形状都有一个可学习 latent vector，decoder
将 `latent + xyz` 映射为 SDF 值。

## 工具脚本

生成新飞机：

```bash
python scripts/generate_new_planes.py -n 5
python scripts/generate_new_planes.py -n 10 -o my_output
```

可视化 mesh：

```bash
python scripts/visualize_compare.py single file.ply
python scripts/visualize_compare.py
python scripts/visualize_compare.py compare mesh1.ply mesh2.ply
```

多视角渲染：

```bash
python scripts/render_planes.py
```

## TTT / LoRA 扩展

后续 TTT/LoRA 研究包位于 `ttt_deepsdf/`，包含 DeepSDF 与 TTT 的结果表、图、
评估脚本、Curriculum DeepSDF 说明和 SOTA baseline 规划文档。

三类数据和较大文件托管在 Git 之外，注意这里有两个不同入口：

| 类型 | 用途 | 链接 |
| --- | --- | --- |
| 数据集 / processed data | 三类 airplane/chair/lamp 的 train/test SDF、NormalizationParameters、SurfaceSamples 和 split 文件。 | https://drive.google.com/drive/folders/13GROzOX06VnVvUyttnTEAmkw0to6O36y?usp=sharing |
| 结果 / 模型 artifact | checkpoint、重建 mesh、server snapshot、结果归档和报告快照。 | https://drive.google.com/drive/folders/1EPH4qcBP8OfL0nSVdleFuJZi2a7E6H4a?usp=sharing |

详细数据/结果说明：
- [REPRODUCIBILITY_START_HERE.md](ttt_deepsdf/docs/REPRODUCIBILITY_START_HERE.md)
- [DATA_AND_ARTIFACTS.md](ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md)
- [GOOGLE_DRIVE_ARTIFACT_MANIFEST_2026-04-27.md](ttt_deepsdf/docs/GOOGLE_DRIVE_ARTIFACT_MANIFEST_2026-04-27.md)

入口文档：`ttt_deepsdf/README.zh-CN.md`。

## 当前飞机实验结果

| 指标 | 值 |
| --- | ---: |
| 测试样本数 | 456 |
| Chamfer Distance (x1000) | 约 0.36 |
| 重建完成率 | 100% |

示例图片：

| 文件 | 说明 |
| --- | --- |
| `images/generated_planes_view.png` | 6 个生成飞机 |
| `images/generated_vs_real.png` | 生成结果与真实重建对比 |
| `images/renders/*.png` | 单个飞机的四视角渲染 |

## 常见问题

### 显存或内存不足

降低 `specs.json` 中的 batch size，例如：

```json
"ScenesPerBatch": 2
```

### 训练太慢

有 GPU 时优先使用 GPU。首次验证可将 `SamplesPerScene` 降到 `8192`。

### 生成质量较差

增加训练 epoch，或使用更高的 marching-cubes 分辨率，例如 `N=256`。

### 查看训练进度

```bash
python scripts/plot_log.py --log models/Logs/Logs.pth
```

## 后续方向

1. 更长训练，例如 1000+ epoch。
2. 更高 marching-cubes 分辨率，例如 256 或 512。
3. 更多 ShapeNet 类别。
4. 条件 DeepSDF 生成。
5. Latent interpolation 和形状渐变。
