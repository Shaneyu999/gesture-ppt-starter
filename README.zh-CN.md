# Gesture PPT Starter

[English](README.md) | [简体中文](README.zh-CN.md)

一个 **实时手势识别 + PPT/视频控制** Python 项目。

通过普通摄像头识别四种手势，并将手势转换为播放器或演示文稿的键盘操作：

| 手势 | 默认操作 | 按键 |
| --- | --- | --- |
| 张开手掌 | 播放/暂停 | `space` |
| 剪刀手 | 下一张/快进 | `right` |
| 点赞 | 上一张/快退 | `left` |
| 握拳 | 静音/取消静音 | `m` |

> 安全默认：程序默认只预览识别结果，不发送键盘按键。只有显式添加 `--enable-controls` 才会实际控制当前窗口。

## 项目特点

- 使用普通 USB 摄像头或笔记本摄像头；
- 使用 MobileNetV3-Small，小型、训练速度快；
- 支持摄像头批量采集训练图片；
- 支持训练、单图预测和实时摄像头推理；
- 使用连续帧和冷却时间减少误触发；
- 手势到按键的映射可以修改；
- 默认预览模式，避免误操作；
- 包含合成数据脚本，没有摄像头也能检查训练流程；
- 包含项目介绍、基础知识、Demo 教程和 GitHub 教程。

## 项目结构

```text
gesture-ppt-starter/
├── README.md
├── pyproject.toml
├── requirements.txt
├── configs/
│   ├── labels.json
│   └── actions.json
├── data/
│   ├── README.md
│   └── gestures/
│       ├── train/
│       └── val/
├── docs/
│   ├── 01_project_introduction.md
│   ├── 02_basics.md
│   ├── 03_github_guide.md
│   └── 04_demo_guide.md
├── scripts/
│   ├── check_camera.py
│   └── make_smoke_data.py
├── src/gesture_ppt/
│   ├── actions.py
│   ├── camera.py
│   ├── cli.py
│   ├── config.py
│   ├── data.py
│   ├── metrics.py
│   ├── model.py
│   ├── predictor.py
│   ├── stability.py
│   └── train.py
└── tests/
```

## 环境要求

- Python 3.10 或更高版本；
- 推荐 Python 3.11 或 3.12，OpenCV 兼容性通常更好；
- 普通 USB 摄像头或笔记本摄像头；
- 训练：CPU 可以完成小数据集训练，GPU 更快；
- 控制功能：Windows、macOS 或 Linux 桌面环境；
- 实际控制时，目标 PPT 或视频播放器必须处于前台。

## 快速开始

### 1. 创建虚拟环境

```powershell
cd C:\Users\Shane\Documents\Codex\2026-09-24\new-chat\outputs\gesture-ppt-starter

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

如果不想每次激活虚拟环境，可以直接使用：

```powershell
.\.venv\Scripts\python.exe -m gesture_ppt.cli --help
```

### 2. 检查摄像头

```powershell
gesture-ppt --help
python scripts\check_camera.py --camera 0
```

窗口出现后，按 `Q` 或 `Esc` 退出。

如果打不开摄像头，可以尝试：

```powershell
python scripts\check_camera.py --camera 1
```

### 3. 采集训练图片

先采集“张开手掌”。运行后按空格开始或暂停，按 Q 退出：

```powershell
gesture-ppt capture `
  --output data\gestures\train `
  --label palm `
  --session desk-01 `
  --count 150 `
  --interval 3
```

依次采集四类手势：

```powershell
gesture-ppt capture --output data\gestures\train --label palm --session desk-01
gesture-ppt capture --output data\gestures\train --label peace --session desk-01
gesture-ppt capture --output data\gestures\train --label thumbs_up --session desk-01
gesture-ppt capture --output data\gestures\train --label fist --session desk-01
```

建议每类至少采集 100～300 张，并改变：

- 手的距离和角度；
- 背景和光照；
- 左手和右手；
- 摄像头位置；
- 不同人员。

验证集要使用另一个 session，最好也改变背景和光照：

```powershell
gesture-ppt capture --output data\gestures\val --label palm --session evening-01 --count 40
gesture-ppt capture --output data\gestures\val --label peace --session evening-01 --count 40
gesture-ppt capture --output data\gestures\val --label thumbs_up --session evening-01 --count 40
gesture-ppt capture --output data\gestures\val --label fist --session evening-01 --count 40
```

### 4. 没有摄像头时检查流程

生成合成手势图：

```powershell
python scripts\make_smoke_data.py --output data\smoke
```

用合成图训练一个很小模型：

```powershell
gesture-ppt train `
  --train-dir data\smoke\train `
  --val-dir data\smoke\val `
  --output-dir runs\smoke_model `
  --epochs 2 `
  --freeze-backbone `
  --no-pretrained `
  --device cpu
```

这些图片只用于检查代码，不表示真实手势识别效果。

### 5. 训练真实手势模型

```powershell
gesture-ppt train `
  --train-dir data\gestures\train `
  --val-dir data\gestures\val `
  --output-dir runs\gesture_model `
  --epochs 12 `
  --batch-size 16 `
  --freeze-backbone `
  --class-weights `
  --device cpu
```

有 NVIDIA GPU 时：

```powershell
gesture-ppt train `
  --train-dir data\gestures\train `
  --val-dir data\gestures\val `
  --output-dir runs\gesture_model `
  --epochs 20 `
  --batch-size 32 `
  --device cuda
```

训练完成后得到：

```text
runs/gesture_model/best.pt
runs/gesture_model/metrics.json
```

### 6. 单图预测

```powershell
gesture-ppt predict `
  --image data\gestures\val\peace\peace_evening-01_00000.jpg `
  --checkpoint runs\gesture_model\best.pt `
  --device cpu
```

### 7. 实时预览，不实际控制

先把摄像头窗口和手势模型跑起来：

```powershell
gesture-ppt run `
  --checkpoint runs\gesture_model\best.pt `
  --actions configs\actions.json `
  --camera 0 `
  --device cpu `
  --roi 0.65 `
  --predict-every 2 `
  --stable-frames 5 `
  --cooldown 1.5
```

屏幕上会显示：

```text
Gesture: peace 0.91
Action: next (right)
Controls: PREVIEW ONLY
Stable: 5
FPS: 24.5
```

此模式不会发送任何按键。

### 8. 实际控制 PPT 或视频

确认预览识别稳定后，再加上：

```powershell
gesture-ppt run `
  --checkpoint runs\gesture_model\best.pt `
  --actions configs\actions.json `
  --camera 0 `
  --device cpu `
  --window-title "PowerPoint" `
  --enable-controls
```

`--window-title` 是可选的。如果填写，程序发送按键前会先尝试激活匹配的窗口，这样摄像头预览不需要一直占用前台。窗口标题可以通过任务栏或 `pyautogui` 的窗口列表确认。

使用步骤：

1. 启动 PPT 放映或打开视频；
2. 再运行带 `--enable-controls` 的命令；
3. 保持 PPT 或播放器处于前台；
4. 把手放在摄像头画面中央区域；
5. 保持同一手势约 5 帧；
6. 需要停止时切回摄像头窗口，按 `Q`。

如果 PPT 需要前台，而摄像头预览也要显示，建议：

- 使用双屏，把预览放在第二屏；
- 或者先测试动作，再切回 PPT；
- 或者在 `configs/actions.json` 中改成你需要的按键。

## 修改手势和按键

标签文件：

```text
configs/labels.json
```

按键映射文件：

```text
configs/actions.json
```

例如，把剪刀手改成 PageDown：

```json
{
  "peace": {
    "action": "next",
    "key": "pagedown",
    "description": "下一张幻灯片"
  }
}
```

修改标签后，需要重新采集对应数据并重新训练。

## 防误触机制

程序不会识别到一次手势就立刻按键，而是要求：

1. 置信度大于 `--min-confidence`；
2. 同一个手势连续出现 `--stable-frames` 次；
3. 距离上一次相同手势动作超过 `--cooldown` 秒。

建议初始值：

```text
--min-confidence 0.60
--stable-frames 5
--cooldown 1.5
```

如果误触发较多：

- 提高 `--min-confidence`；
- 增加 `--stable-frames`；
- 增加 `--cooldown`；
- 增加背景变化和困难样本；
- 重新训练模型。

## 运行逻辑测试

不需要摄像头即可检查稳定触发和动作映射：

```powershell
gesture-ppt simulate `
  --sequence palm,peace,thumbs_up,fist `
  --stable-frames 3 `
  --cooldown 0.5
```

这个命令默认也只输出预览结果。

## 运行测试

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## 常见问题

### 找不到摄像头

- 关闭占用摄像头的会议软件；
- 尝试 `--camera 1`；
- 检查系统摄像头权限。

### OpenCV 安装失败

建议使用 Python 3.11 或 3.12 创建虚拟环境。部分最新的 Python 小版本可能暂时没有 OpenCV 预编译包。

### 控制功能没有反应

- 是否添加了 `--enable-controls`；
- PPT 或播放器是否处于前台；
- 按键是否被目标程序识别；
- 在 `configs/actions.json` 中检查按键名。

### 识别总跟着背景变化

- 增加不同背景数据；
- 让手占据画面中央更大区域；
- 调整 `--roi`；
- 避免训练集中某一手势总是出现在固定背景。

## 隐私和安全

- 本项目只识别手势，不存储身份信息；
- 摄像头图片可能包含人物和背景，不要上传到公开仓库；
- `data/gestures/`、`runs/` 和模型权重默认已被 `.gitignore` 排除；
- 实际键盘控制可能影响当前窗口，请先使用预览模式测试；
- 不要让程序在没有人工监督的情况下控制重要系统。

## 当前限制

- 只支持四种固定手势；
- 对快速移动、遮挡和强逆光可能不稳定；
- 仅通过键盘控制，不直接调用 PowerPoint API；
- 训练数据来自摄像头，模型容易受到背景和光照影响；
- 合成图片只能用于流程测试，不能用于效果评价。

## 下一步扩展

1. 加入更多手势，例如 OK、数字手势、左右挥手；
2. 使用 MediaPipe 手部关键点提升旋转和遮挡鲁棒性；
3. 增加实时手部检测框；
4. 加入手势序列，例如“先握拳再点赞”；
5. 使用 ONNX Runtime 加速部署；
6. 加入演示视频和 Gradio/Streamlit 控制面板。

## 许可证

代码采用 MIT License。第三方模型、数据集和库分别遵循各自许可证。
