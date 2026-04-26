# DeepSDF CPU-only 服务器数据预处理复现手册

本文档说明如何在一台 CPU-only、无显示器的 Linux 服务器上复现 DeepSDF 数据
预处理流程，将 ShapeNet 原始 mesh 转换为 DeepSDF 使用的 SDF 采样数据。

文档中的主机地址、用户名、私钥路径和工作目录均使用占位符。实际执行时，请替换
为自己的服务器信息，避免把私有账号或机器地址提交到公开仓库。

## 1. 适用范围

本流程适用于以下场景：

- 服务器没有 NVIDIA GPU，`nvidia-smi` 不存在或不可用。
- 服务器没有物理显示器，需要通过 `xvfb` 和 Mesa 软件渲染运行预处理程序。
- 目标任务是运行 DeepSDF 原始仓库的 `preprocess_data.py`，并生成
  `SdfSamples/*.npz` 和 `NormalizationParameters/*.json`。

推荐系统环境：

| 项目 | 建议 |
| --- | --- |
| OS | Ubuntu 22.04 或 24.04 |
| CPU | 2 cores 以上 |
| Memory | 8 GB 以上更稳 |
| Compiler | `gcc-12` / `g++-12` |
| Pangolin | `v0.6` |
| Python env | Conda environment with Python 3.6 for the original DeepSDF code |

## 2. 目录约定

后续命令使用以下占位符：

| 占位符 | 含义 |
| --- | --- |
| `<SERVER_HOST>` | 服务器 IP 或域名 |
| `<SERVER_USER>` | SSH 登录用户名 |
| `<SSH_KEY>` | 本地 SSH 私钥路径 |
| `<WORKDIR>` | 服务器上的工作目录，例如 `~/deepsdf_setup` |
| `<SHAPENET_DIR>` | ShapeNetCore.v2 根目录 |

示例连接命令：

```bash
ssh -i <SSH_KEY> <SERVER_USER>@<SERVER_HOST>
```

非交互连通性测试：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 -i <SSH_KEY> \
  <SERVER_USER>@<SERVER_HOST> "echo ok"
```

预期输出为 `ok`。

## 3. 服务器基础检查

登录服务器后先确认系统、资源和 GPU 状态：

```bash
cat /etc/os-release | head -n 6
lscpu | egrep 'Model name|CPU\(s\)|Thread\(s\) per core|Core\(s\) per socket|Socket\(s\)'
free -h
nvidia-smi
```

如果 `nvidia-smi` 不存在，说明当前是 CPU-only 环境。这不影响数据预处理，但
需要启用无头渲染配置。

## 4. 安装基础软件

```bash
sudo apt-get update -y
sudo apt-get install -y \
  build-essential cmake git wget curl unzip pkg-config \
  libglew-dev libgl1-mesa-dev libegl1-mesa-dev libglu1-mesa-dev \
  mesa-utils xvfb zlib1g-dev gcc-12 g++-12
```

关键依赖说明：

- `xvfb`：在无显示器环境中提供虚拟 X11。
- Mesa 相关库：提供 CPU 软件 OpenGL 渲染。
- `zlib1g-dev`：`cnpy`/DeepSDF 编译时常见依赖。
- `gcc-12`/`g++-12`：在 Ubuntu 24.04 上比默认较新的编译器组合更稳定。

后续编译不需要修改系统默认编译器，直接在命令前指定：

```bash
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12
```

## 5. 编译 C++ 依赖

以下命令默认在 `<WORKDIR>` 下执行。

```bash
mkdir -p <WORKDIR>
cd <WORKDIR>
```

### 5.1 CLI11

```bash
git clone https://github.com/CLIUtils/CLI11 --recursive
cd CLI11
mkdir -p build
cd build
cmake ..
cmake --build . -j2
sudo cmake --install .
```

### 5.2 Eigen3 3.4.0

```bash
cd <WORKDIR>
wget https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
tar xvf eigen-3.4.0.tar.gz
cd eigen-3.4.0
mkdir -p build
cd build
cmake ..
cmake --build . -j2
sudo cmake --install .
```

### 5.3 Pangolin v0.6

DeepSDF 原始预处理工具依赖 Pangolin。建议使用 `v0.6`，不要直接使用较新的
`v0.9.x`，否则在部分服务器上可能遇到 OpenGL 或 ABI 兼容问题。

```bash
cd <WORKDIR>
git clone https://github.com/stevenlovegrove/Pangolin.git --recursive
cd Pangolin
git checkout v0.6
git submodule update --init --recursive
```

Ubuntu 24.04 默认 Python 版本较新，Pangolin v0.6 的 Python/pybind 组件可能编译
失败。数据预处理不依赖 Pangolin Python 绑定，因此建议关闭相关模块：

```bash
rm -rf build
mkdir build
cd build
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 cmake \
  -DBUILD_PANGOLIN_FFMPEG=OFF \
  -DBUILD_PANGOLIN_PYTHON=OFF \
  -DBUILD_PYPANGOLIN_MODULE=OFF \
  ..
cmake --build . -j2
sudo cmake --install .
sudo ldconfig
```

### 5.4 nanoflann

```bash
cd <WORKDIR>
git clone https://github.com/jlblancoc/nanoflann
cd nanoflann
mkdir -p build
cd build
cmake ..
cmake --build . -j2
sudo cmake --install .
```

如旧代码查找 `nanoflann.hpp` 失败，可确认头文件是否位于
`/usr/local/include/nanoflann.hpp`。

## 6. 编译 DeepSDF

```bash
cd <WORKDIR>
git clone https://github.com/facebookresearch/DeepSDF.git
cd DeepSDF/third-party
git clone https://github.com/rogersce/cnpy.git
```

然后编译 DeepSDF：

```bash
cd <WORKDIR>/DeepSDF
rm -rf build
mkdir build
cd build
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 cmake -DCMAKE_CXX_STANDARD=17 ..
cmake --build . -j2
sudo cmake --install .
```

检查二进制是否生成：

```bash
ls -la <WORKDIR>/DeepSDF/bin
```

应至少包含：

- `PreprocessMesh`
- `SampleVisibleMeshSurface`

## 7. Python 环境

DeepSDF 原始代码较老，建议使用独立 conda 环境：

```bash
cd ~
wget -O miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda.sh -b -p ~/miniconda3
source ~/miniconda3/etc/profile.d/conda.sh
conda create -n deepsdf_py36 python=3.6 -y
conda activate deepsdf_py36
```

安装 CPU 版本依赖：

```bash
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

CPU-only 环境下预期 `cuda_available=False`。

## 8. 运行数据转换

### 8.1 设置无头渲染变量

```bash
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330
```

### 8.2 小样本验证

正式转换前建议先跑一个最小 split，确认编译、OpenGL 和 Python 环境都可用。

```bash
cd <WORKDIR>/DeepSDF
source ~/miniconda3/etc/profile.d/conda.sh
conda activate deepsdf_py36

xvfb-run -s "-screen 0 1024x768x24" python preprocess_data.py \
  --data_dir data_cpu_test \
  --source <SHAPENET_DIR> \
  --name ShapeNetV2 \
  --split examples/splits/sv2_chair_one_test.json \
  --skip --threads 1
```

### 8.3 正式数据集转换

```bash
xvfb-run -s "-screen 0 1024x768x24" python preprocess_data.py \
  --data_dir data \
  --source <SHAPENET_DIR> \
  --name ShapeNetV2 \
  --split examples/splits/sv2_chairs_train.json \
  --skip --threads 1
```

CPU 较少或内存较小时，优先使用 `--threads 1` 保证稳定。

## 9. 验证输出

不要只依据终端日志判断成功，必须检查文件产物：

```bash
find <WORKDIR>/DeepSDF/data_cpu_test -type f | head
```

应出现类似路径：

```text
.../SdfSamples/ShapeNetV2/<class_id>/<instance_id>.npz
```

检查 `.npz` 内容：

```bash
python - <<'PY'
from pathlib import Path
import numpy as np

root = Path('data_cpu_test/SdfSamples/ShapeNetV2')
sample = next(root.glob('*/*.npz'))
d = np.load(sample)
print(sample)
print(d.files)
print('pos', d['pos'].shape, d['pos'].dtype)
print('neg', d['neg'].shape, d['neg'].dtype)
PY
```

预期至少包含：

- `pos (N, 4)`
- `neg (M, 4)`

## 10. 常见问题与修复

### `preprocess_data.py` 有日志但没有 `.npz`

DeepSDF 原始 `preprocess_data.py` 内部调用子进程时不总是严格检查
`returncode`。如果目录里只有 `.datasources.json`，请直接执行
`./bin/PreprocessMesh` 或查看子进程输出，定位真实错误。

### `PreprocessMesh` 出现 segmentation fault

常见原因是 Pangolin、编译器和 OpenGL 环境组合不兼容。建议确认：

1. 使用 `Pangolin v0.6`。
2. 使用 `gcc-12/g++-12` 重新编译 Pangolin 和 DeepSDF。
3. 使用 `xvfb-run`。
4. 设置 `LIBGL_ALWAYS_SOFTWARE=1` 等 Mesa 软件渲染变量。

### Pangolin v0.6 编译时报 Python/pybind 错误

典型错误包括 `invalid use of incomplete type 'PyFrameObject'`。关闭 Pangolin
Python 组件即可：

```bash
-DBUILD_PANGOLIN_PYTHON=OFF
-DBUILD_PYPANGOLIN_MODULE=OFF
```

### `Permission denied (publickey)`

检查 SSH 用户、私钥路径和服务器授权配置。不要把真实私钥路径或服务器地址写入
公开文档。

### `nvidia-smi not found`

CPU-only 服务器上的正常现象，不影响数据转换。继续使用 `xvfb-run + Mesa`
软件渲染配置。

## 11. 最小复现脚本

将下面内容保存为 `run_deepsdf_cpu_test.sh`，并替换占位符：

```bash
#!/usr/bin/env bash
set -euo pipefail

WORKDIR="<WORKDIR>"
SHAPENET_DIR="<SHAPENET_DIR>"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate deepsdf_py36

cd "${WORKDIR}/DeepSDF"

export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330

xvfb-run -s "-screen 0 1024x768x24" python preprocess_data.py \
  --data_dir data_cpu_test \
  --source "${SHAPENET_DIR}" \
  --name ShapeNetV2 \
  --split examples/splits/sv2_chair_one_test.json \
  --skip --threads 1

find data_cpu_test -type f | sed -n '1,50p'
```

执行：

```bash
chmod +x run_deepsdf_cpu_test.sh
./run_deepsdf_cpu_test.sh
```

## 12. 复现检查清单

1. SSH 能正常登录服务器。
2. 系统依赖和 `gcc-12/g++-12` 已安装。
3. `Pangolin v0.6` 已关闭 Python/FFMPEG 并成功安装。
4. DeepSDF 已用同一编译器组合重新编译。
5. Conda 环境 `deepsdf_py36` 可用。
6. `xvfb` 和 Mesa 软件渲染环境变量已设置。
7. 小样本 split 能生成 `SdfSamples/*.npz`。
8. `.npz` 中包含 `pos` 和 `neg` 两组 SDF 样本。
