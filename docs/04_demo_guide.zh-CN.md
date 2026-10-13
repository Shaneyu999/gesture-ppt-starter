# 三分钟 Demo 指南

## 演示目标

让观众理解下面的完整过程：

```text
摄像头画面
  -> 手势识别
  -> 稳定手势判断
  -> 动作映射
  -> PPT/视频收到键盘操作
```

## 演示前准备

1. 准备好四种手势的训练数据并完成模型训练；
2. 打开 PPT 放映或视频播放器；
3. 打开摄像头，保持手和背景清晰；
4. 先运行不带 `--enable-controls` 的预览命令；
5. 确认四种手势都能稳定识别；
6. 再运行带 `--enable-controls` 的命令。

预览命令：

```powershell
gesture-ppt run `
  --checkpoint runs\gesture_model\best.pt `
  --actions configs\actions.json `
  --camera 0 `
  --device cpu
```

实际控制命令：

```powershell
gesture-ppt run `
  --checkpoint runs\gesture_model\best.pt `
  --actions configs\actions.json `
  --camera 0 `
  --device cpu `
  --window-title "PowerPoint" `
  --enable-controls
```

## 演示脚本

### 第一步：介绍任务

可以这样说明：

> 这个系统使用普通摄像头识别手势。为了让操作更可靠，程序要求同一手势连续稳定出现几帧，并且两次操作之间有时间间隔。默认只预览，不会真的控制电脑。

### 第二步：展示不控制模式

依次做四种手势：

- 张开手掌；
- 剪刀手；
- 点赞；
- 握拳。

指着画面说明：

- `Gesture`：识别结果；
- `Action`：准备执行的动作；
- `Controls: PREVIEW ONLY`：当前不会发送按键；
- `Stable`：手势已经稳定的帧数。

### 第三步：切换控制模式

把 PPT 或视频切到前台，然后展示：

- 张开手掌：播放或暂停；
- 剪刀手：下一张；
- 点赞：上一张；
- 握拳：静音。

### 第四步：说明防误触

解释以下机制：

1. 置信度阈值；
2. 连续稳定帧数；
3. 相同动作的冷却时间；
4. 键盘控制默认关闭。

### 第五步：展示失败案例

可以故意展示：

- 只出现一帧的手势不会触发；
- 太低置信度不会触发；
- 背景变化时可能误判；
- 快速移动时识别不稳定。

这可以引出后续改进方向：

- 收集更多背景数据；
- 使用手部关键点；
- 增加时序模型；
- 调整阈值和动作映射。

## 演示环境建议

- 摄像头高度接近眼睛；
- 手放在画面中央；
- 光源从正面照向手，避免强逆光；
- 背景尽量简洁；
- PPT 使用第二屏，摄像头预览放在第一屏；
- 关闭会占用摄像头的会议软件。

## 现场备用方案

如果摄像头或目标软件失效，可以使用：

```powershell
gesture-ppt simulate `
  --sequence palm,peace,thumbs_up,fist `
  --stable-frames 3
```

或者只展示已经保存的单图预测结果和模型评估指标。不要在当前环境中临时重新训练大模型。
