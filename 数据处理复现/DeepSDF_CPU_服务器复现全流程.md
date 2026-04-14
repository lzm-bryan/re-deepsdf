# DeepSDF 在 CPU-only 服务器上的完整复现手册（连接、部署、排障、验证）

## 0. 文档目标

本文档面向“从零复现 DeepSDF 数据转换（ShapeNet -> SDF）”的同学，目标是让他人按步骤直接复现你当前已经跑通的流程。

文档覆盖内容：

1. 如何从 Windows 连接服务器。
2. 如何在 Ubuntu 24.04 CPU-only 服务器部署环境。
3. 如何从失败状态修到可用状态。
4. 如何验证转换成功。
5. 如何做“原始数据 vs 转换后数据”的可视化对比。
6. 常见报错与对策。

---

## 1. 本次复现的基线信息

### 1.1 本地环境

- 本地系统：Windows（PowerShell）
- 工作目录：`E:\作业`
- SSH 私钥：`E:\作业\lzm897.pem`

### 1.2 服务器信息

- 登录地址：`13.239.96.213`
- 登录用户：`ubuntu`
- 主机名：`ip-172-31-39-0`
- 系统：`Ubuntu 24.04.4 LTS`
- CPU：`2 vCPU`
- 内存：`7.6 GiB`
- GPU：无（`nvidia-smi` 不存在）
- 系统盘：约 `48G`

### 1.3 数据与代码位置（服务器）

- ShapeNet 数据：`/home/ubuntu/datasets/ShapeNetCore.v2`
- DeepSDF 工程：`/home/ubuntu/deepsdf_setup/DeepSDF`
- 编译依赖目录：`/home/ubuntu/deepsdf_setup`

### 1.4 参考文章（你提供）

- CSDN（新文）：<https://blog.csdn.net/weixinhum/article/details/149218796>
- CSDN（旧文，本地保存页对应原文）：`qq_38677322/article/details/110957634`

---

## 2. 先说结论（复现结果）

- 结论：**CPU-only 可以做 DeepSDF 的数据转换**，但必须满足正确版本组合与无头渲染设置。
- 最终成功产物（示例样本）：
  - `/home/ubuntu/deepsdf_setup/DeepSDF/data_cpu_test_v2/SdfSamples/ShapeNetV2/03001627/1006be65e7bc937e9141f9b58470d646.npz`
- 成功验证：`.npz` 内有 `pos/neg` 两组 SDF 样本。

---

## 3. 从 Windows 连接服务器

在本地 PowerShell 执行：

```powershell
ssh -i "E:\作业\lzm897.pem" ubuntu@13.239.96.213
```

首次连接会写入 known_hosts。若需非交互测试连通性：

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=8 -i "E:\作业\lzm897.pem" ubuntu@13.239.96.213 "echo ok"
```

预期输出：`ok`

---

## 4. 服务器基础检查（建议先做）

登录后先确认是 CPU-only 场景：

```bash
cat /etc/os-release | head -n 6
lscpu | egrep 'Model name|CPU\(s\)|Thread\(s\) per core|Core\(s\) per socket|Socket\(s\)'
free -h
nvidia-smi
```

- 如果 `nvidia-smi` 不存在，说明无 NVIDIA GPU。

---

## 5. 基础软件安装

```bash
sudo apt-get update -y
sudo apt-get install -y \
  build-essential cmake git wget curl unzip pkg-config \
  libglew-dev libgl1-mesa-dev libegl1-mesa-dev libglu1-mesa-dev \
  mesa-utils xvfb zlib1g-dev
```

说明：

- `xvfb`：无显示器时提供虚拟 X11。
- `mesa` 系列：软件 OpenGL 渲染。
- `zlib`：`cnpy`/DeepSDF 编译常见依赖。

---

## 6. GCC/G++ 版本处理（关键）

根据文章实践，Ubuntu 24.04 上建议使用 `gcc-12/g++-12`：

```bash
sudo apt-get install -y gcc-12 g++-12
```

后续编译时不改系统默认版本，直接在命令前指定：

- `CC=/usr/bin/gcc-12`
- `CXX=/usr/bin/g++-12`

---

## 7. 安装/编译四个 C++ 依赖

以下都在 `/home/ubuntu/deepsdf_setup` 下进行。

### 7.1 CLI11

```bash
cd ~/deepsdf_setup
git clone https://github.com/CLIUtils/CLI11 --recursive
cd CLI11
mkdir -p build && cd build
cmake ..
cmake --build . -j2
sudo cmake --install .
```

### 7.2 Eigen3（3.4.0）

```bash
cd ~/deepsdf_setup
wget https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
tar xvf eigen-3.4.0.tar.gz
cd eigen-3.4.0
mkdir -p build && cd build
cmake ..
cmake --build . -j2
sudo cmake --install .
```

### 7.3 Pangolin（必须重点看）

#### 7.3.1 正确版本

必须用 `v0.6`，不要用新版本（例如 v0.9.x）。

```bash
cd ~/deepsdf_setup
git clone https://github.com/stevenlovegrove/Pangolin.git --recursive
cd Pangolin
git checkout v0.6
git submodule update --init --recursive
```

#### 7.3.2 Ubuntu 24.04 上的关键编译参数

在本次环境里，如果直接编会遇到 Python 3.12 + pybind 的错误，需要关闭 Pangolin Python 相关模块：

```bash
cd ~/deepsdf_setup/Pangolin
rm -rf build
mkdir build && cd build
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 cmake \
  -DBUILD_PANGOLIN_FFMPEG=OFF \
  -DBUILD_PANGOLIN_PYTHON=OFF \
  -DBUILD_PYPANGOLIN_MODULE=OFF \
  ..
cmake --build . -j2
sudo cmake --install .
sudo ldconfig
```

说明：

- `-DBUILD_PANGOLIN_FFMPEG=OFF`：兼容性更高，文章同样建议关闭。
- `-DBUILD_PANGOLIN_PYTHON=OFF`：规避 pybind 在 Python 3.12 上的不兼容报错。

### 7.4 nanoflann

```bash
cd ~/deepsdf_setup
git clone https://github.com/jlblancoc/nanoflann
cd nanoflann
mkdir -p build && cd build
cmake ..
cmake --build . -j2
sudo cmake --install .
```

如需兼容旧代码 include，可检查 `/usr/local/include/nanoflann.hpp` 路径。

---

## 8. 编译 DeepSDF

```bash
cd ~/deepsdf_setup
git clone https://github.com/facebookresearch/DeepSDF.git
cd DeepSDF/third-party
git clone https://github.com/rogersce/cnpy.git
```

可按文章修改 `ShaderProgram.cpp` 的语句（一些环境下可避免 shader 相关问题）。

然后编译：

```bash
cd ~/deepsdf_setup/DeepSDF
rm -rf build
mkdir build && cd build
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 cmake -DCMAKE_CXX_STANDARD=17 ..
cmake --build . -j2
sudo cmake --install .
```

检查二进制：

```bash
ls -la ~/deepsdf_setup/DeepSDF/bin
```

预期看到：

- `PreprocessMesh`
- `SampleVisibleMeshSurface`

---

## 9. Python 环境（数据转换）

建议使用 conda 独立环境：

```bash
cd ~
wget -O miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda.sh -b -p ~/miniconda3
source ~/miniconda3/etc/profile.d/conda.sh
conda create -n deepsdf_py36 python=3.6 -y
conda activate deepsdf_py36
```

安装依赖：

```bash
# CPU-only 环境建议直接装 CPU torch 1.1.0
pip install torch==1.1.0 torchvision==0.3.0
pip install numpy scipy scikit-image trimesh plyfile
```

验证：

```bash
python - <<'PY'
import torch
print('torch=', torch.__version__)
print('cuda_available=', torch.cuda.is_available())
PY
```

预期：`cuda_available=False`

---

## 10. 运行数据转换（核心命令）

### 10.1 无头渲染环境变量（CPU-only 必须）

```bash
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330
```

### 10.2 小样本验证（强烈建议先跑 1 个）

示例 split：`examples/splits/sv2_chair_one_test.json`

```bash
cd ~/deepsdf_setup/DeepSDF
source ~/miniconda3/etc/profile.d/conda.sh
conda activate deepsdf_py36

xvfb-run -s "-screen 0 1024x768x24" python preprocess_data.py \
  --data_dir data_cpu_test_v2 \
  --source ~/datasets/ShapeNetCore.v2 \
  --name ShapeNetV2 \
  --split examples/splits/sv2_chair_one_test.json \
  --skip --threads 1
```

### 10.3 正式数据集转换

例如训练集：

```bash
xvfb-run -s "-screen 0 1024x768x24" python preprocess_data.py \
  --data_dir data \
  --source ~/datasets/ShapeNetCore.v2 \
  --name ShapeNetV2 \
  --split examples/splits/sv2_chairs_train.json \
  --skip --threads 1
```

注意：本机只有 2 vCPU，建议 `--threads 1` 或 `2`，优先稳定。

---

## 11. 如何判断“真的成功”

必须检查**文件产物**，不要只看脚本是否退出。

```bash
find ~/deepsdf_setup/DeepSDF/data_cpu_test_v2 -type f | head
```

应出现类似路径：

`.../SdfSamples/ShapeNetV2/<class>/<instance>.npz`

再检查 npz 内容：

```bash
python - <<'PY'
import numpy as np
p='/home/ubuntu/deepsdf_setup/DeepSDF/data_cpu_test_v2/SdfSamples/ShapeNetV2/03001627/1006be65e7bc937e9141f9b58470d646.npz'
d=np.load(p)
print(d.files)
print('pos', d['pos'].shape, d['pos'].dtype)
print('neg', d['neg'].shape, d['neg'].dtype)
PY
```

预期至少包含：

- `pos (N,4)`
- `neg (M,4)`

---

## 12. 这次真实遇到的问题与修复顺序（关键复现经验）

### 问题 1：初始环境“看起来跑了”，但没有 `.npz`

表现：

- `preprocess_data.py` 有日志，但目录里只有 `.datasources.json`。

原因：

- `preprocess_data.py` 内部用 `subprocess.Popen(...).wait()`，没有检查 `returncode`，子进程失败时主脚本不一定报错退出。

修复：

- 直接单独执行 `./bin/PreprocessMesh` 定位真实崩溃原因。

### 问题 2：`PreprocessMesh` 段错误（Segmentation fault）

表现：

- 大量 OpenGL 警告后崩溃。

原因：

- 版本组合不对：当时是 `Pangolin v0.9.5 + gcc13`，与文章实践不一致。

修复：

1. 切到 `Pangolin v0.6`。
2. 使用 `gcc-12/g++-12` 编译 Pangolin 与 DeepSDF。
3. 运行时启用 `xvfb + Mesa software render`。

### 问题 3：Pangolin v0.6 在 Ubuntu 24.04 编译报 Python/pybind 错

典型报错：

- `invalid use of incomplete type 'PyFrameObject'`

原因：

- pybind 老版本与 Python 3.12 API 兼容问题。

修复：

- 编译 Pangolin 时关闭 Python 组件：
  - `-DBUILD_PANGOLIN_PYTHON=OFF`
  - `-DBUILD_PYPANGOLIN_MODULE=OFF`

结论：

- 数据转换不依赖 Pangolin Python 绑定，关闭后不影响本任务。

---

## 13. 可视化对比（用于人工验收）

目的：

- 左图看原始 mesh 顶点分布。
- 中图看转换后 SDF `pos/neg` 点云分布。
- 右图看 SDF 数值分布。

本次生成位置（本地）：

- `C:\temp\deepsdf_compare\deepsdf_before_after_compare.png`

可视化结论示例：

- 原始 OBJ 顶点数：`756`
- SDF 输出：`pos=302205`，`neg=163337`
- `pos` 第四列以正值为主，`neg` 第四列以负值为主，符合预期。

---

## 14. 一份可直接执行的最小复现脚本（服务器端）

把下面内容保存为 `run_deepsdf_cpu_test.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

source ~/miniconda3/etc/profile.d/conda.sh
conda activate deepsdf_py36

cd ~/deepsdf_setup/DeepSDF

export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330

xvfb-run -s "-screen 0 1024x768x24" python preprocess_data.py \
  --data_dir data_cpu_test_v2 \
  --source ~/datasets/ShapeNetCore.v2 \
  --name ShapeNetV2 \
  --split examples/splits/sv2_chair_one_test.json \
  --skip --threads 1

find data_cpu_test_v2 -type f | sed -n '1,50p'
```

执行：

```bash
chmod +x run_deepsdf_cpu_test.sh
./run_deepsdf_cpu_test.sh
```

---

## 15. 常见问题速查

### Q1：`Permission denied (publickey)`

A：

- 确认用户名是 `ubuntu`。
- 确认私钥权限和路径正确。
- 命令里显式 `-i` 指向 `.pem`。

### Q2：`Please login as the user "ubuntu" rather than the user "root"`

A：

- 该机器禁止 root 直登，改用 `ubuntu`。

### Q3：`nvidia-smi not found`

A：

- 这是 CPU-only 机器正常现象，不影响数据转换。

### Q4：`glxinfo: not found`

A：

- 装 `mesa-utils`；但核心是 `xvfb-run + MESA` 环境变量。

### Q5：`preprocess_data.py` 似乎成功但没输出文件

A：

- 直接手动跑 `./bin/PreprocessMesh`，检查是否崩溃。

### Q6：`Segmentation fault`（PreprocessMesh）

A：

1. 确认 `Pangolin v0.6`。
2. 确认 `gcc-12/g++-12` 重新编译。
3. 使用 `xvfb-run`。
4. 加 `LIBGL_ALWAYS_SOFTWARE=1` 等软件渲染变量。

### Q7：Pangolin 编译 pybind/Python 错

A：

- 关闭 Python 模块编译参数（见第 7.3.2 节）。

---

## 16. 复现实验建议（针对 2 vCPU / 7.6G）

1. 先 1 个样本验证，再扩展 split。
2. 线程不要开高，`--threads 1` 最稳。
3. 每次只改一个变量（版本、编译器、环境变量），便于定位问题。
4. 关注产物文件，不要只看终端“看似成功”的日志。

---

## 17. 本次最终可复现状态（记录）

- DeepSDF 二进制存在：
  - `/home/ubuntu/deepsdf_setup/DeepSDF/bin/PreprocessMesh`
  - `/home/ubuntu/deepsdf_setup/DeepSDF/bin/SampleVisibleMeshSurface`
- 样本转换成功产物：
  - `/home/ubuntu/deepsdf_setup/DeepSDF/data_cpu_test_v2/SdfSamples/ShapeNetV2/03001627/1006be65e7bc937e9141f9b58470d646.npz`
- 可视化对比图（本地）：
  - `C:\temp\deepsdf_compare\deepsdf_before_after_compare.png`

---

## 18. 给复现者的最短执行清单

1. `ssh` 登录服务器（ubuntu 用户）。
2. 安装依赖包和 `gcc-12/g++-12`。
3. 编译 `Pangolin v0.6`（关闭 Python/FFMPEG）。
4. 用 gcc12 重编 `DeepSDF`。
5. 激活 `deepsdf_py36` 环境。
6. 设置 `MESA + xvfb` 参数。
7. 跑 `preprocess_data.py` 小样本。
8. 检查 `SdfSamples/*.npz` 的真实产物。

按上面 8 步做，基本就能稳定复现本次数据处理流程。
