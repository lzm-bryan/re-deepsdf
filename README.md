# DeepSDF 飞机重建实验 - 4.13 planes类 600epoch

> 版本：planes类 600epoch
> 日期：2026-04-13
> 模型：DeepSDF Auto-Decoder (Epoch 600)
> 数据集：ShapeNet V2 (02691156 - 飞机)

---

## 一键运行

```bash
# 1. 克隆仓库
git clone https://github.com/lzm-bryan/re-deepsdf.git
cd re-deepsdf

# 2. 下载数据（见下方链接）
# 下载后解压到 data/ 目录

# 3. 生成新飞机
python scripts/generate_new_planes.py -n 5

# 4. 查看结果
python scripts/visualize_compare.py single generated/GeneratedPlanes/generated_plane_001.ply
```

---

## 数据下载

数据存储在 Google Drive（因文件过大），下载后解压到本仓库 `data/` 目录：

| 数据 | 大小 | 下载链接 |
|------|------|----------|
| 训练数据 | 795 KB | [training_4.13planes-600epoch.zip](https://drive.google.com/file/d/1fkHA9ZclgHxMAdm_jM-GYwCZ9MdiLC7B/view?usp=sharing) |
| 测试数据 | 3.0 GB | [test_4.13planes-600epoch.zip](https://drive.google.com/file/d/19ENGz3Cnxp_7HmjjBLcPgkSR23UpwqC-/view?usp=sharing) |
| 重建结果 | 261 MB | [reconstructions_4.13planes-600epoch.zip](https://drive.google.com/file/d/11KQy6ca7o8MuPxGZBU5PWwAhzOVQhw9n/view?usp=sharing) |
| 隐向量 | 583 KB | [latentcodes_4.13planes-600epoch.zip](https://drive.google.com/file/d/1WeusBcG0clPVxzfozuSA0M84I8EKtSN7/view?usp=sharing) |

**解压后目录结构：**
```
data/
├── TrainingData/NormalizationParameters/ShapeNetV2/02691156/  # 627个训练样本
├── TestData/SdfSamples/ShapeNetV2/02691156/                   # 456个测试样本
├── TestData/NormalizationParameters/ShapeNetV2/02691156/
└── Reconstructions/600/Meshes/ShapeNetV2/02691156/            # 456个重建mesh
```

**或自行从 ShapeNet 下载**：https://shapenet.org/

---

## 目录结构

```
├── configs/                          # 实验配置
│   └── specs.json
├── models/                          # 模型文件
│   ├── ModelParameters/600.pth     # Decoder权重 (7.4 MB)
│   ├── LatentCodes/600.pth         # 隐向量 (643 KB)
│   └── Logs/Logs.pth              # 训练日志
├── source_code/                     # 源代码
│   ├── src/
│   │   ├── train_deep_sdf.py       # 训练脚本
│   │   ├── reconstruct.py          # 重建脚本
│   │   ├── evaluate.py             # 评估脚本
│   │   └── deep_sdf/              # 工具模块
│   └── networks/
│       └── deep_sdf_decoder.py     # Decoder网络
├── scripts/                         # 工具脚本
│   ├── generate_new_planes.py      # 生成新飞机
│   ├── visualize_compare.py        # 可视化
│   ├── render_planes.py           # 多视角渲染
│   └── visualize_generated_vs_real.py  # 对比图
├── generated/GeneratedPlanes/       # 生成的飞机 (PLY)
├── images/                          # 可视化结果
├── data/                            # 数据（需下载）
└── README.md
```

---

## 实验概述

### 任务
使用 DeepSDF 对 ShapeNet V2 飞机数据进行3D重建，并从随机隐向量生成新飞机。

### 模型配置

| 参数 | 值 |
|------|-----|
| 类型 | Auto-Decoder |
| 隐向量维度 | 256 |
| 网络结构 | [256+3] → 512×4 → 256 → 128 → 1 |
| 训练Epoch | 600 |
| 归一化 | Weight Norm + Layer Norm |

### 评测结果

| 指标 | 值 |
|------|-----|
| Chamfer Distance (×1000) | ~0.36 |
| 重建完成率 | 100% |

---

## 核心原理

### SDF (Signed Distance Function)

```
SDF(p) < 0  →  点在物体内部
SDF(p) = 0  →  点在物体表面
SDF(p) > 0  →  点在物体外部
```

### Auto-Decoder

训练时，隐向量作为可学习参数直接优化：
```python
for each shape:
    latent = optimizable_vector(256)
    for epoch in range(600):
        loss = MSE(decoder(latent, coords), sdf_true)
        optimizer.step()  # 同时优化latent和decoder
```

### 新形状生成

从训练好的隐向量分布随机采样：
```python
z ~ N(mean=-0.000351, std=0.0456)  # 随机隐向量
mesh = decoder(z, coords) → marching_cubes → PLY
```

---

## 工具脚本

### 生成新飞机
```bash
# 生成5个新飞机到 generated/GeneratedPlanes/
python scripts/generate_new_planes.py -n 5

# 指定输出目录
python scripts/generate_new_planes.py -n 10 -o my_planes
```

### 可视化
```bash
# 查看单个mesh
python scripts/visualize_compare.py single file.ply

# 随机显示6个
python scripts/visualize_compare.py

# 对比两个mesh
python scripts/visualize_compare.py compare mesh1.ply mesh2.ply
```

### 多视角渲染
```bash
python scripts/render_planes.py
# 输出到 images/renders/
```

---

## 环境依赖

```bash
pip install torch numpy trimesh matplotlib scikit-image
```

---

## 数据来源

- **ShapeNet V2**: https://shapenet.org/
  - 类别ID: 02691156 (飞机)
  - 需要注册下载

---

## 可视化结果

| 文件 | 说明 |
|------|------|
| images/generated_planes_view.png | 6个生成飞机3D图 |
| images/generated_vs_real.png | 生成 vs 真实重建对比 |
| images/sample_planes.png | 重建样本展示 |
| images/renders/*.png | 每个飞机的4视角渲染 |

---

## 复现建议

1. **训练复现**：需要GPU集群，从 ShapeNet 下载数据，运行 `source_code/src/train_deep_sdf.py`
2. **仅推理**：直接下载模型权重和测试数据，运行 `scripts/generate_new_planes.py`
3. **仅可视化**：下载重建结果 `reconstructions_*.zip`，用 MeshLab 或 Python 查看 PLY 文件

---

## 后续研究

- 更长训练 (1000+ epoch)
- 更高分辨率 (N=256, 512)
- 多类别 (车、船、椅子等)
- 条件DeepSDF
- 隐向量插值动画

---

*文档更新: 2026-04-13*
