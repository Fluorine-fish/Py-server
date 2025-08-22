# 瞳灵智能台灯系统 | Tongling Smart Lamp System

# Py-server

一个为嵌入式/边缘设备和本地网络设计的 Python 服务集合。该仓库组合了：摄像头与视频流管理、情绪检测（RKNN/ONNX）、音频唤醒/语音、串口设备控制、灯控示例、Web API 与本地 Web 前端等模块。

> 说明：README 基于仓库当前代码结构（`app.py`, `modules/`, `Emotion_Detector/`, `webserver/`, `Audio/` 等）整理，某些入口点按项目惯例做了合理假设（见下文“假设”）。

## 主要功能

- 摄像头管理与实时视频流。
- 基于 ONNX / RKNN 的情绪检测模块（支持模型转换与 RKNN 加速）。
- 本地音频唤醒与简单语音助手（`Audio/`）。
- 串口设备与外设控制（`serial_handler.py`, `modules/serial_module.py`）。
- 灯控示例与控制模块（`modules/lamp_control_module.py`）。
- 简易 Web/API 服务与前端（`app.py`, `routes.py`, `webserver/`）。
- 定时任务/守护进程（`guardian_scheduler.py`）。

## 仓库结构速览

- `app.py` — 项目的一个可运行入口（HTTP 服务/后端）。
- `light_server.py` — 另一个与灯控或实时流相关的服务（项目中存在多个入口，请按需要选择）。
- `routes.py` — 路由定义（有备份 `routes.py.bak`）。
- `modules/` — 各种功能模块（摄像头、情绪检测、灯控、串口、视频流等）。
- `Emotion_Detector/` — 与模型转换、RKNN/ONNX、情绪检测实现相关的代码与模型目录。
- `Audio/` — 语音与唤醒相关脚本与资源（含 Snowboy、voice_assistant）。
- `webserver/` 与 `WebServer/` — 前后端服务、移动端/PC 前端相关代码。
- `tests/` 或若干测试文件（如 `test_emotion_integration.py`, `test_websocket.py`）。
- 部署/工具脚本：`create_hotspot.sh`, `ios_hotspot.sh`, `detect_audio.sh`, `wifi_hotspot.service` 等。
- 环境依赖：`requirements.txt`, `environment.yml`。

## 先决条件

- 推荐 Python 3.9+（仓库包含针对多版本的 pyc 编译产物）。
- 若使用 RKNN 相关功能，目标设备通常为 aarch64（仓库内存在 `rknn_toolkit_lite2-2.3.2-...aarch64.whl`），需要在相应硬件或交叉环境中安装。

## 快速开始（开发）

1. 克隆仓库并进入目录：

```bash
git clone <your-repo-url>
cd Py-server
```

2. 建议使用虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -U pip
```

3. 安装依赖：

```bash
# 推荐：使用 environment.yml 创建 conda 环境（如果你使用 conda）
conda env create -f environment.yml
conda activate <env-name>

# 或（通用）：
pip install -r requirements.txt
```

4. 运行后端服务（假定 `app.py` 为主入口；如果你的部署使用 `webserver/server.py` 或 `light_server.py`，请替换为相应脚本）：

```bash
python app.py
# 或
python webserver/server.py
```

5. 打开浏览器访问本地前端或 API（默认地址与端口请参照启动日志或代码中的配置，常见为 `http://localhost:5000` 或 `http://0.0.0.0:5000`）。

## 运行测试

仓库内包含一些测试脚本，使用 pytest 运行：

```bash
pip install pytest
pytest -q
```

注意：部分测试可能依赖硬件（摄像头、串口或 RKNN 设备），在无相关硬件时会失败或被跳过。

## 情绪检测与 RKNN

- `Emotion_Detector/` 包含模型转换脚本（`onnx2rknn.py`, `t2onnx.py` 等）和使用 RKNN 的示例（`EmotionDetector_RKNN.py`）。
- 仓库中包含一个 RKNN 工具包 wheel（面向 aarch64）：`rknn_toolkit_lite2-2.3.2-cp39-...aarch64.whl`。如果需在开发机上运行 RKNN，请确保平台/CPU 架构与 wheel 相匹配，或在目标设备上安装。

简单转换流程示例（假设你已有 ONNX 模型）：

```bash
# 把 onnx 转 rknn（示例）
python Emotion_Detector/onnx2rknn.py --input model.onnx --output model.rknn
```

（脚本参数和用法请参阅对应文件头部注释或代码）

## 热点与网络设置

- 仓库包含 TCP/IP 热点与 hostapd 示例配置：`create_hotspot.sh`, `ios_hotspot.sh`, `hostapd.conf`, `wifi_hotspot.service`。
- 使用这些脚本前请先阅读并根据你系统的网络配置调整（脚本通常需要 root 权限）。

## 部署提示（树莓派 / 边缘设备）

- 若部署在 ARM 设备（如 RK、树莓派等），建议使用系统自带的 Python 与相应的 wheel 或交叉编译工具安装依赖。
- 确保串口设备权限（如 `/dev/tty*`）和摄像头设备权限。
- 若使用 GPU/NNPU（RKNN），参考 `Emotion_Detector/` 中的说明与 RKNN 文档。

## 常见问题与故障排查

- 服务未启动或端口被占用：确认没有其他进程占用端口，检查启动日志。
- 串口通信失败：确认设备路径、波特率设置与权限（可能需要加入 dialout 组或使用 sudo）。
- 摄像头不能打开：检查设备路径、驱动和权限。
- RKNN wheel 无法安装：确认目标 CPU 架构匹配（aarch64）或在目标设备上安装。

## 开发与贡献

欢迎通过 issue 与 pull request 贡献改进。建议：

- 提交清晰的 issue 描述问题或改进点。
- 针对新特性或重构，先在 issue 中讨论设计。

## 假设（若遇到不一致请校正）

- 假设 `app.py` 或 `webserver/server.py` 可以作为启动服务的入口；如果你有特定的启动脚本或容器化配置，请根据实际替换命令。
- 假设项目运行在类 Unix 系统（Linux），热点脚本和 systemd service 适用于 Linux 环境。

## 许可证

项目包含 `LICENSE` 文件，请查阅该文件以了解授权和使用条款。

---


简介（精简）

一个集成摄像头管理、情绪检测（ONNX/RKNN）、音频唤醒、串口与灯控控制的本地 Python 服务集合，适用于边缘设备与本地网络部署。

快速安装

```bash
# 建议使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

运行（常用入口）

```bash
# 启动主服务（若使用其它入口请替换）
python app.py
# 或（如使用 webserver）
python webserver/server.py
```

测试

```bash
pip install pytest
pytest -q
```

重要文件

- `app.py`、`light_server.py`：常见启动脚本。
- `modules/`：功能模块（摄像头、情绪检测、串口、灯控等）。
- `Emotion_Detector/`：模型转换与 RKNN 使用示例。
- `Audio/`：语音/唤醒相关代码。

注意与假设

- 如果使用 RKNN，请在 aarch64 目标设备上安装对应的 wheel。仓库内含 RKNN wheel（面向 aarch64）。
- 热点脚本（如 `create_hotspot.sh`）与 systemd service 仅适用于类 Linux 系统，使用前请检查并修改配置。

许可证

见仓库中的 `LICENSE` 文件。
