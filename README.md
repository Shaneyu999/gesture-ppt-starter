# Gesture PPT Starter

[English](README.md) | [简体中文](README.zh-CN.md)

A **real-time hand gesture recognition and PPT/video control** project in Python.

It uses a normal webcam to recognize four hand gestures and convert them into keyboard actions for a presentation or media player:

| Gesture | Default action | Key |
| --- | --- | --- |
| Open palm | Play or pause | `space` |
| Peace sign | Next slide or forward | `right` |
| Thumbs-up | Previous slide or rewind | `left` |
| Fist | Mute or unmute | `m` |

> Safety default: the program only previews predictions by default. It sends keyboard input only when `--enable-controls` is explicitly provided.

## Features

- Works with a normal USB or laptop webcam;
- Uses MobileNetV3-Small for lightweight gesture classification;
- Supports webcam data collection and custom training;
- Supports single-image prediction and real-time webcam inference;
- Uses confidence thresholds, stable frames, and cooldown periods to reduce false triggers;
- Allows gesture-to-key mappings to be edited in a JSON file;
- Runs in preview-only mode by default;
- Includes a synthetic data generator for checking the training pipeline without a camera;
- Includes unit tests and a GitHub Actions workflow.

## Project structure

```text
gesture-ppt-starter/
├── README.md
├── README.zh-CN.md
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


## Requirements

- Python 3.10 or later;
- Python 3.11 or 3.12 is recommended for better OpenCV compatibility;
- A USB webcam or laptop camera;
- CPU training is sufficient for a small dataset, while a GPU is faster;
- A desktop environment for real-time camera and keyboard control;
- The target presentation or media player must be available as a foreground or focusable window.

## Quick start

### 1. Create a virtual environment

```powershell
git clone https://github.com/Shaneyu999/gesture-ppt-starter.git
cd gesture-ppt-starter

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

If you do not want to activate the environment, use the virtual environment Python directly:

```powershell
.\.venv\Scripts\python.exe -m gesture_ppt.cli --help
```

### 2. Check the camera

```powershell
gesture-ppt --help
python scripts\check_camera.py --camera 0
```

Press `Q` or `Esc` to close the preview.

If camera index 0 does not work, try:

```powershell
python scripts\check_camera.py --camera 1
```

### 3. Collect training images

Start with the open palm gesture. Press Space to start or pause capture, and press Q to exit:

```powershell
gesture-ppt capture `
  --output data\gestures\train `
  --label palm `
  --session desk-01 `
  --count 150 `
  --interval 3
```

Collect all four gestures:

```powershell
gesture-ppt capture --output data\gestures\train --label palm --session desk-01
gesture-ppt capture --output data\gestures\train --label peace --session desk-01
gesture-ppt capture --output data\gestures\train --label thumbs_up --session desk-01
gesture-ppt capture --output data\gestures\train --label fist --session desk-01
```

Aim for at least 100 to 300 images per gesture. Vary:

- Hand distance and angle;
- Background and lighting;
- Left and right hands;
- Camera position;
- Different participants when possible.

Collect validation data in a separate session:

```powershell
gesture-ppt capture --output data\gestures\val --label palm --session evening-01 --count 40
gesture-ppt capture --output data\gestures\val --label peace --session evening-01 --count 40
gesture-ppt capture --output data\gestures\val --label thumbs_up --session evening-01 --count 40
gesture-ppt capture --output data\gestures\val --label fist --session evening-01 --count 40
```

Do not randomly split consecutive frames from one recording between training and validation. Keep each session separate to avoid data leakage.

### 4. Test the pipeline without a camera

Generate synthetic gesture images:

```powershell
python scripts\make_smoke_data.py --output data\smoke
```

Train a small test model:

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


### 5. Train a real gesture model

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

With an NVIDIA GPU:

```powershell
gesture-ppt train `
  --train-dir data\gestures\train `
  --val-dir data\gestures\val `
  --output-dir runs\gesture_model `
  --epochs 20 `
  --batch-size 32 `
  --device cuda
```

The training outputs are:

```text
runs/gesture_model/best.pt
runs/gesture_model/metrics.json
```

### 6. Predict a single image

```powershell
gesture-ppt predict `
  --image data\gestures\val\peace\peace_evening-01_00000.jpg `
  --checkpoint runs\gesture_model\best.pt `
  --device cpu
```

### 7. Camera-based command collection

Load only the gesture model and open the camera window:

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

The output is as follows:

```text
Gesture: peace 0.91
Action: next (right)
Controls: PREVIEW ONLY
Stable: 5
FPS: 24.5
```

No keyboard input is sent in this mode.

### 8. Control PowerPoint or video playback

After the preview is stable, enable keyboard control:

```powershell
gesture-ppt run `
  --checkpoint runs\gesture_model\best.pt `
  --actions configs\actions.json `
  --camera 0 `
  --device cpu `
  --window-title "PowerPoint" `
  --enable-controls
```

The optional `--window-title` argument attempts to focus a matching window before sending a key. If it is omitted, keep the target PowerPoint or media player focused manually.

Recommended workflow:

1. Start the PowerPoint slideshow or open the video;
2. Start the command with `--enable-controls`;
3. Keep the target player available in the foreground or use a second display;
4. Place your hand in the center region of the camera view;
5. Hold the gesture for several frames;
6. Switch back to the camera preview and press `Q` to stop the program.

## Configure gestures and keys

Gesture labels are defined in:

```text
configs/labels.json
```

Keyboard mappings are defined in:

```text
configs/actions.json
```

For example, to map the peace sign to PageDown:

```json
{
  "peace": {
    "action": "next",
    "key": "pagedown",
    "description": "Next slide"
  }
}
```

Changing the labels requires collecting new data and retraining the model.

## False-trigger prevention

The system does not send a key from a single prediction. It requires all of the following:

1. Confidence above `--min-confidence`;
2. The same gesture for `--stable-frames` consecutive frames;
3. At least `--cooldown` seconds since the previous action of the same type.

Recommended starting values:

```text
--min-confidence 0.60
--stable-frames 5
--cooldown 1.5
```

If false triggers occur frequently:

- Increase `--min-confidence`;
- Increase `--stable-frames`;
- Increase `--cooldown`;
- Add more background and difficult training samples;
- Retrain the classifier.

## Test the action logic

The action mapping can be tested without a camera:

```powershell
gesture-ppt simulate `
  --sequence palm,peace,thumbs_up,fist `
  --stable-frames 3 `
  --cooldown 0.5
```

This command only previews actions unless `--enable-controls` is explicitly supplied.

## Run the tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Troubleshooting

### Camera not found

- Close applications that may be using the camera;
- Try `--camera 1`;
- Check camera permissions in the operating system.

### OpenCV installation failed

Use Python 3.11 or 3.12 to create the virtual environment. Some of the latest Python versions may not have matching OpenCV wheels yet.

### Keyboard control does not work

- Confirm that `--enable-controls` is present;
- Confirm that PowerPoint or the media player is in the foreground, or use `--window-title`;
- Check whether the target application recognizes the configured key;
- Check the key names in `configs/actions.json`.

### Predictions follow the background

- Collect more background variation;
- Keep the hand larger in the center region;
- Adjust `--roi`;
- Avoid training data where one gesture always appears against the same background.

## Privacy and safety

- The project recognizes gestures and does not store identity information;
- Camera images may contain people and private backgrounds, so do not upload them to a public repository;
- `data/gestures/`, `runs/`, and model checkpoints are excluded by `.gitignore`;
- Keyboard control can affect the active window, so test in preview mode first;
- Do not let the program control important applications without supervision.

## Current limitations

- Only four fixed static gestures are supported;
- Recognition may degrade with fast movement, occlusion, or strong backlighting;
- Control uses keyboard events and does not call the PowerPoint API directly;
- Training data comes from the camera, so the model can be sensitive to background and lighting;
- The synthetic images are only for pipeline testing and cannot be used to evaluate real performance.

## License

The source code is released under the MIT License. Third-party models, datasets, and libraries follow their respective licenses.
