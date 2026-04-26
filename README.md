# DeepSDF 飞机重建实验 - 4.13 planes类 600epoch

> 版本：planes类 600epoch
> 日期：2026-04-13
> 模型：DeepSDF Auto-Decoder (Epoch 600)
> 数据集：ShapeNet V2 (02691156 - 飞机)

---

## 项目入口速览

这个仓库不只是一份单独的 DeepSDF 代码，它同时保存了复现实验、数据处理记录和后续 TTT/LoRA 扩展实验。建议先按下面的入口找对应内容：

| 你想做什么 | 应该看哪里 | 说明 |
| --- | --- | --- |
| 跑通基础 DeepSDF 飞机重建 | 本 README | 包含环境、数据下载、生成、可视化、训练和评估命令。 |
| 查看数据从哪里来、当时如何处理 | [`数据处理复现/`](数据处理复现/) | 历史数据处理记录、CPU/服务器复现说明、参考链接和离线网页备份。一般不需要先读。 |
| 查看 TTT / LoRA 改进实验 | [`ttt_deepsdf/`](ttt_deepsdf/) | TTT 代码、DeepSDF/TTT 结果表、小图、复现指南、Curriculum DeepSDF 和 SOTA baseline 文档。 |

如果你是第一次打开这个仓库，推荐顺序是：先读本 README 跑通基础复现；需要追溯数据时再看 `数据处理复现/`；需要看课程/论文方向的 TTT 结果时再进入 `ttt_deepsdf/README.md`。

## 仓库结构

```text
re-deepsdf/
├── configs/           # DeepSDF 飞机实验配置
├── generated/         # 小型生成 mesh 示例
├── images/            # 可视化图片
├── models/            # 小型模型参数和 latent code 示例
├── scripts/           # 生成、渲染、可视化脚本
├── source_code/       # DeepSDF 训练、重建、评估代码
├── ttt_deepsdf/       # TTT/LoRA DeepSDF 研究包
└── 数据处理复现/      # 数据处理过程记录与参考资料
```

大体量数据、完整 checkpoint、全量重建 mesh 不建议直接放进 Git；需要时从 README 或 `ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md` 中的 Google Drive 链接下载。

---

## 一键运行（仅推理）

```bash
# 1. 克隆仓库
git clone https://github.com/lzm-bryan/re-deepsdf.git
cd re-deepsdf

# 2. 下载数据
# 从 Google Drive 下载并解压 data/ 目录（见下方链接）

# 3. 生成新飞机
python scripts/generate_new_planes.py -n 5

# 4. 查看结果
python scripts/visualize_compare.py single generated/GeneratedPlanes/generated_plane_001.ply
```

---

## 完整复现训练（可选）

### 环境要求

```bash
pip install torch numpy trimesh matplotlib scikit-image open3d
# 或
conda install pytorch numpy trimesh matplotlib scikit-image
```

### 数据准备

从 Google Drive 下载并解压到本仓库 `data/` 目录：

| 数据 | 大小 | 说明 | 下载链接 |
|------|------|------|----------|
| 训练数据 (TrainingData) | 4.1 GB | **完整训练数据 (SdfSamples + NormalizationParameters)** | [train_4.13planes-600epoch.zip](https://drive.google.com/file/d/1KCqG-tOYm3H92792S17m-JFwLCmFdS0k/view?usp=sharing) |
| 测试数据 (TestData) | 3.0 GB | SDF采样 + 归一化参数 | [test_4.13planes-600epoch.zip](https://drive.google.com/file/d/19ENGz3Cnxp_7HmjjBLcPgkSR23UpwqC-/view?usp=sharing) |
| 重建结果 (Reconstructions) | 261 MB | 456个重建mesh | [reconstructions_4.13planes-600epoch.zip](https://drive.google.com/file/d/11KQy6ca7o8MuPxGZBU5PWwAhzOVQhw9n/view?usp=sharing) |
| 隐向量 (LatentCodes) | 583 KB | 627个训练样本隐向量 | [latentcodes_4.13planes-600epoch.zip](https://drive.google.com/file/d/1WeusBcG0clPVxzfozuSA0M84I8EKtSN7/view?usp=sharing) |

解压后目录结构：
```
data/
├── SdfSamples/ShapeNetV2/02691156/      # 627个训练样本SDF (.npz)
├── NormalizationParameters/ShapeNetV2/02691156/  # 归一化参数 (.json)
├── TestData/SdfSamples/ShapeNetV2/02691156/      # 456个测试样本SDF (.npz)
└── TestData/NormalizationParameters/ShapeNetV2/02691156/  # 归一化参数 (.json)
```

#### 方式2：从 ShapeNet 原始数据生成

1. **下载 ShapeNet V2**
   - 注册: https://shapenet.org/
   - 下载类别: 02691156 (飞机)
   - 需要原始 .obj mesh 文件

2. **生成 SDF 采样数据**
   ```bash
   # 使用 DeepSDF 的预处理脚本
   python source_code/src/generate_training_meshes.py \
       --data-source /path/to/shapenet \
       --shape-category 02691156 \
       --output-dir ./data/SdfSamples
   ```

### 配置文件

`configs/specs.json` 已配置好默认参数，数据路径使用相对路径 `./data/`。

### 训练

```bash
python source_code/src/train_deep_sdf.py \
    --experiment-name planes_600epoch \
    --data-path ./data \
    --epochs 600
```

### 评估

```bash
# 重建测试集
python source_code/src/reconstruct.py \
    --experiment-name planes_600epoch \
    --checkpoint models/ModelParameters/600.pth

# 计算指标
python source_code/src/evaluate.py \
    --experiment-name planes_600epoch \
    --reconstruction-dir ./data/Reconstructions
```

---

## 数据说明

### 数据目录结构（下载后）

```
data/
├── TrainingData/
│   └── NormalizationParameters/ShapeNetV2/02691156/  # 627个训练样本
│       ├── 1a6f615e8b1b5ae4ce388047.json
│       └── ...
├── TestData/
│   ├── SdfSamples/ShapeNetV2/02691156/      # 456个测试样本 (.npz)
│   │   ├── 1a6f615e8b1b5ae4ce388047.npz
│   │   └── ...
│   └── NormalizationParameters/ShapeNetV2/02691156/  # 归一化参数
└── Reconstructions/600/Meshes/ShapeNetV2/02691156/  # 重建结果 (.ply)
```

### SDF 数据格式

每个 .npz 文件包含：
- `pos`: 正采样点 (N × 4) - [x, y, z, sdf]
- `neg`: 负采样点 (M × 4) - [x, y, z, sdf]

---

## 核心代码说明

### 网络架构 (deep_sdf_decoder.py)

```python
Decoder(
    latent_size=256,     # 隐向量维度
    dims=[512×8],        # 8层全连接
    latent_in=[4],       # 隐向量在第4层注入
    dropout=[0-7],       # 每层dropout
    weight_norm=True     # 权重归一化
)
```

### 训练策略

| 参数 | 值 | 说明 |
|------|-----|------|
| Batch Size | 4 | 每批次场景数 |
| Samples/Scene | 16384 | 每场景采样点数 |
| Learning Rate | 0.0005 | 初始学习率 |
| LR Schedule | Step | 每500epoch减半 |
| Epochs | 1000+ | 训练轮数 |
| Code Regularization | 1e-4 | 隐向量L2正则 |

### Auto-Decoder vs Auto-Encoder

```
Auto-Encoder:  Image → [Encoder] → Latent → [Decoder] → SDF
Auto-Decoder:  Latent(可学习) + XYZ → [Decoder] → SDF
```

DeepSDF使用Auto-Decoder，训练时隐向量作为可学习参数直接优化。

---

## 工具脚本

### 生成新飞机
```bash
# 生成5个新飞机
python scripts/generate_new_planes.py -n 5

# 指定输出目录
python scripts/generate_new_planes.py -n 10 -o my_output
```

### 可视化
```bash
# 查看单个mesh
python scripts/visualize_compare.py single file.ply

# 随机显示6个重建样本
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

## Google Drive 数据链接

| 数据 | 大小 | 说明 | 下载链接 |
|------|------|------|----------|
| **训练SDF采样** | 4.1 GB | **完整训练数据，可直接复现训练** | [train_4.13planes-600epoch.zip](https://drive.google.com/file/d/1KCqG-tOYm3H92792S17m-JFwLCmFdS0k/view?usp=sharing) |
| 测试数据 | 3.0 GB | 456个测试样本SDF采样 | [test_4.13planes-600epoch.zip](https://drive.google.com/file/d/19ENGz3Cnxp_7HmjjBLcPgkSR23UpwqC-/view?usp=sharing) |
| 重建结果 | 261 MB | 456个重建mesh (.ply) | [reconstructions_4.13planes-600epoch.zip](https://drive.google.com/file/d/11KQy6ca7o8MuPxGZBU5PWwAhzOVQhw9n/view?usp=sharing) |
| 隐向量 | 583 KB | 627个训练样本隐向量 | [latentcodes_4.13planes-600epoch.zip](https://drive.google.com/file/d/1WeusBcG0clPVxzfozuSA0M84I8EKtSN7/view?usp=sharing) |

TTT/LoRA 三类别数据和大文件归档见：[`ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md`](ttt_deepsdf/docs/DATA_AND_ARTIFACTS.md)。

---

## 实验结果

| 指标 | 值 |
|------|-----|
| 测试样本数 | 456 |
| Chamfer Distance (×1000) | ~0.36 |
| 重建完成率 | 100% |

### 可视化示例

| 文件 | 说明 |
|------|------|
| images/generated_planes_view.png | 6个生成飞机3D图 |
| images/generated_vs_real.png | 生成 vs 真实重建对比 |
| images/renders/*.png | 每个飞机的4视角渲染 |

---

## 常见问题

### Q: 内存不足？
```bash
# 减小batch size
# 修改 specs.json: "ScenesPerBatch": 2
```

### Q: 训练太慢？
- 使用GPU加速
- 减少 `SamplesPerScene` (建议8192起步)

### Q: 生成质量差？
- 增加训练epoch (当前600，建议1000+)
- 提高Marching Cubes分辨率 (N=256)

### Q: 如何查看训练进度？
```bash
python scripts/plot_log.py --log models/Logs/Logs.pth
```

---

## 后续研究方向

1. **更长训练**: Epoch 1000+
2. **更高分辨率**: N=256, 512
3. **多类别**: 车(02958340)、船(04530566)
4. **条件生成**: 类别条件DeepSDF
5. **隐向量插值**: 形状渐变动画

---

*文档更新: 2026-04-13*
