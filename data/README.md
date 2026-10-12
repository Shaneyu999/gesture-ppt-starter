# Gesture data layout

Recommended structure:

```text
data/gestures/
  train/
    palm/
    peace/
    thumbs_up/
    fist/
  val/
    palm/
    peace/
    thumbs_up/
    fist/
```

Use the capture command to collect images:

```powershell
gesture-ppt capture --output data/gestures/train --label palm --session desk-01
gesture-ppt capture --output data/gestures/val --label palm --session evening-01
```

Keep different sessions, backgrounds, people, and lighting between training and
validation. Avoid placing consecutive frames from one recording into both
training and validation sets.
