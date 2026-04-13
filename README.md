# DeepSDF 飞机重建实验结果 - 4.13 planes类 600epoch

> 实验日期：2026-04-13
> 版本：planes类 600epoch
> 模型：DeepSDF Auto-Decoder (Epoch 600)
> 数据集：ShapeNet V2 (02691156 - 飞机)
> 评测样本数：456

---

## 数据下载说明

**⚠️ 数据文件过大（~3.9GB），存储在 Google Drive**

### Google Drive 下载地址

| 文件 | 大小 | 下载链接 |
|------|------|----------|
| 训练数据 (TrainingData) | 795 KB | [training_4.13planes-600epoch.zip](https://drive.google.com/file/d/1fkHA9ZclgHxMAdm_jM-GYwCZ9MdiLC7B/view?usp=sharing) |
| 测试数据 (TestData) | 3.0 GB | [test_4.13planes-600epoch.zip](https://drive.google.com/file/d/19ENGz3Cnxp_7HmjjBLcPgkSR23UpwqC-/view?usp=sharing) |
| 重建结果 (Reconstructions) | 261 MB | [reconstructions_4.13planes-600epoch.zip](https://drive.google.com/file/d/11KQy6ca7o8MuPxGZBU5PWwAhzOVQhw9n/view?usp=sharing) |
| 隐向量 (LatentCodes) | 583 KB | [latentcodes_4.13planes-600epoch.zip](https://drive.google.com/file/d/1WeusBcG0clPVxzfozuSA0M84I8EKtSN7/view?usp=sharing) |

**或自行准备 ShapeNet V2**: https://shapenet.org/

### 数据目录结构
```
data/                    # 请从 Google Drive 下载此文件夹
├── TrainingData/        # 训练数据 (~2.3 MB)
├── TestData/            # 测试数据 (~3.2 GB)
└── Reconstructions/     # 重建结果 (~681 MB)
```

---

## 目录结构

```
DeepSDF_Results_2026-04-13/
├── configs/                          # 配置文件
│   └── specs.json                    # 实验配置
│
├── models/                           # 模型文件
│   ├── ModelParameters/
│   │   └── 600.pth                  # Epoch 600 模型权重 (7.4 MB)
│   ├── LatentCodes/
│   │   └── 600.pth                  # 627个隐向量 (643 KB)
│   └── Logs/
│       └── Logs.pth                 # 训练日志 (373 KB)
│
├── source_code/                      # 源代码
│   ├── src/
│   │   ├── train_deep_sdf.py        # 训练脚本
│   │   ├── reconstruct.py           # 重建脚本（隐向量优化）
│   │   ├── evaluate.py              # 评估脚本
│   │   ├── generate_training_meshes.py
│   │   ├── plot_log.py
│   │   └── deep_sdf/               # deep_sdf模块
│   └── networks/
│       └── deep_sdf_decoder.py      # Decoder网络定义
│
├── generated/                        # 生成结果
│   └── GeneratedPlanes/             # 6个生成的飞机 (PLY格式)
│
├── scripts/                          # 工具脚本
│   ├── generate_new_planes.py       # 生成新飞机 (从随机隐向量)
│   ├── visualize_compare.py         # 可视化mesh
│   ├── visualize_generated_vs_real.py  # 生成vs真实对比图
│   └── render_planes.py            # 多视角渲染
│
├── images/                           # 可视化图片
│   ├── generated_planes_view.png        # 6个生成飞机3D图
│   ├── generated_vs_real.png            # 生成vs真实对比
│   ├── sample_planes.png                # 重建样本展示
│   └── renders/                         # 多视角渲染图
│
├── 服务器登录信息.md                  # 服务器访问信息
└── README.md                        # 本文档
```

---

## 快速开始

### 1. 下载数据
```bash
# 从 Google Drive 下载 data/ 文件夹
# 放置在此 README.md 同级目录下
```

### 2. 生成新飞机
```bash
# 生成5个新飞机
python scripts/generate_new_planes.py -n 5

# 查看结果
python scripts/visualize_compare.py single generated/GeneratedPlanes/generated_plane_001.ply
```

### 3. 查看重建结果
```bash
python scripts/visualize_compare.py
```

---

## 1. 实验概述

### 1.1 任务背景

使用 DeepSDF (Deep Signed Distance Function) 对 ShapeNet V2 数据集中的飞机 (02691156) 进行3D形状重建。

**DeepSDF核心思想**：通过神经网络学习一个隐式函数 `F(z, x) → SDF值`，其中：
- `z` 是形状的256维隐向量
- `x` 是3D空间中的任意坐标点
- 返回值是该点到物体表面的有符号距离

### 1.2 模型架构

| 参数 | 值 |
|------|-----|
| 类型 | Auto-Decoder (自解码器) |
| 隐向量维度 | 256 |
| 网络结构 | [256+3] → 512 → 512 → 512 → 512 → 256 → 128 → 1 |
| Dropout | 0-4层, p=0.2 |
| 归一化 | Weight Norm + Layer Norm |
| 训练Epoch | 600 |

### 1.3 评测结果

| 指标 | 值 |
|------|-----|
| 测试样本数 | 456 |
| Chamfer Distance (×1000) | ~0.36 |
| 平均顶点数量 | ~10,000/mesh |
| 重建完成率 | 100% |

---

## 2. 核心技术原理

### 2.1 SDF (Signed Distance Function)

SDF定义空间中任意点到物体表面的最短距离：

```
SDF(p) < 0  →  点在物体内部
SDF(p) = 0  →  点在物体表面
SDF(p) > 0  →  点在物体外部
```

### 2.2 Auto-Decoder 架构

训练时，隐向量作为可学习参数直接优化：
```python
for each shape:
    latent = optimizable_vector(256)  # 初始化隐向量
    for epoch in range(600):
        sdf_pred = decoder(latent, coords)
        loss = MSE(sdf_pred, sdf_true)
        optimizer.step()  # 同时优化latent和decoder权重
```

### 2.3 3D重建流程

测试时，已知SDF采样点，重建mesh：
```
1. 固定Decoder权重
2. 随机初始化隐向量 z
3. 优化 z 使 decoder(z, coords) ≈ 真实SDF
4. 用 z + Marching Cubes 提取等值面
```

### 2.4 新形状生成

从学习到的隐向量分布采样：
```python
mean ≈ -0.000351
std ≈ 0.0456
z = np.random.normal(mean, std, size=256)  # 随机隐向量
mesh = decoder(z, coords) → marching_cubes → PLY
```

---

## 3. 模型文件

### 3.1 configs/specs.json
```json
{
  "CodeLength": 256,
  "NetworkSpecs": {
    "dims": [512, 512, 512, 512, 256, 128],
    "dropout": [0, 1, 2, 3, 4],
    "dropout_prob": 0.2,
    "norm_layers": [0, 1, 2, 3, 4],
    "latent_in": [4],
    "weight_norm": true
  },
  "ExperimentName": "planes_default"
}
```

### 3.2 models/ModelParameters/600.pth
- **大小**: 7.4 MB
- **内容**: Decoder所有权重

### 3.3 models/LatentCodes/600.pth
- **大小**: 643 KB
- **结构**: `{'weight': Tensor[627, 256]}`
- **分布**: Mean=-0.000351, Std=0.0456

---

## 4. 工具脚本

### generate_new_planes.py
从随机隐向量生成新飞机：
```bash
python scripts/generate_new_planes.py -n 5 -o output
```

### visualize_compare.py
可视化PLY mesh：
```bash
# 单个mesh
python scripts/visualize_compare.py single file.ply

# 随机显示
python scripts/visualize_compare.py

# 对比两个
python scripts/visualize_compare.py compare mesh1.ply mesh2.ply
```

### render_planes.py
多视角渲染：
```bash
python scripts/render_planes.py
```

---

## 5. 可视化结果

### images/generated_planes_view.png
6个从随机隐向量生成的新飞机3D图。

### images/generated_vs_real.png
- 左: 测试集真实重建
- 右: 随机隐向量生成

### images/renders/
每个飞机的4视角渲染图。

---

## 6. 文件大小

| 目录/文件 | 大小 | 是否上传 |
|-----------|------|----------|
| models/ | 8 MB | ✅ |
| source_code/ | 20 KB | ✅ |
| scripts/ | 20 KB | ✅ |
| images/ | 5 MB | ✅ |
| generated/ | 4 MB | ✅ |
| configs/ | 1 KB | ✅ |
| data/ | ~3.9 GB | ❌ (Google Drive) |
| **总计上传** | **~17 MB** | |

---

## 7. 数据来源

### ShapeNet V2
- 官网: https://shapenet.org/
- 类别: 02691156 (飞机)
- 需要注册下载

### NTU GPU Cluster (可选)
如需复现训练：
- 服务器: 10.96.189.12
- 用户名: zhiming002

---

## 8. 后续研究建议

1. **更长训练**: 当前Epoch 600，可到1000+
2. **更高分辨率**: N=256或512获取更精细mesh
3. **多类别扩展**: 车(02958340)、船(04530566)等
4. **条件DeepSDF**: 结合类别标签实现条件生成
5. **隐向量插值**: 两个形状间平滑过渡动画

---

*文档更新时间: 2026-04-13*
