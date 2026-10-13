# Three-Minute Demo Guide

## Demonstration Objective

Show the complete process:

~~~text
Camera frame
  -> Gesture recognition
  -> Stable-gesture check
  -> Action mapping
  -> Keyboard event received by PowerPoint or video player
~~~

## Preparation

1. Prepare training data for all four gestures and train the model;
2. Open PowerPoint in slideshow mode or open a video player;
3. Start the webcam and keep the hand and background clear;
4. Run the preview command without --enable-controls;
5. Confirm that all four gestures are recognized reliably;
6. Run the command with --enable-controls.

Preview command:

~~~powershell
gesture-ppt run \
  --checkpoint runs\gesture_model\best.pt \
  --actions configs\actions.json \
  --camera 0 \
  --device cpu
~~~

Control command:

~~~powershell
gesture-ppt run \
  --checkpoint runs\gesture_model\best.pt \
  --actions configs\actions.json \
  --camera 0 \
  --device cpu \
  --window-title "PowerPoint" \
  --enable-controls
~~~

## Demonstration Sequence

### Step 1: Introduce the Task

The system uses a normal webcam to recognize gestures. To improve reliability, the same gesture must remain stable for several frames, and repeated actions are separated by a cooldown period. The default mode only previews predictions and does not control the computer.

### Step 2: Show Preview Mode

Perform the four gestures in order:

- Open palm;
- Peace sign;
- Thumbs up;
- Closed fist.

Point out the information displayed on the screen:

- Gesture: recognition result;
- Action: proposed keyboard action;
- Controls: PREVIEW ONLY: no key is currently sent;
- Stable: number of consecutive frames for the current gesture.

### Step 3: Switch to Control Mode

Bring PowerPoint or the video player to the foreground and show:

- Open palm: play or pause;
- Peace sign: next;
- Thumbs up: previous;
- Closed fist: mute.

### Step 4: Explain False-Trigger Prevention

Explain the following mechanisms:

1. Confidence threshold;
2. Stable-frame threshold;
3. Cooldown for repeated actions;
4. Keyboard control disabled by default.

### Step 5: Show Failure Cases

Demonstrate examples such as:

- A gesture shown for only one frame does not trigger;
- A low-confidence prediction does not trigger;
- Background changes may cause errors;
- Fast movement can reduce recognition stability.

These examples lead to future improvements:

- Collect more background data;
- Use hand landmarks;
- Add temporal models;
- Adjust thresholds and action mappings.

## Recommended Demonstration Environment

- Place the camera near eye level;
- Keep the hand in the center of the frame;
- Use frontal lighting and avoid strong backlighting;
- Keep the background simple;
- Use a second display for PowerPoint and keep the camera preview on the primary display;
- Close meeting software that may occupy the camera.

## Fallback Plan

If the camera or target application fails, run:

~~~powershell
gesture-ppt simulate \
  --sequence palm,peace,thumbs_up,fist \
  --stable-frames 3
~~~

Alternatively, show saved single-image predictions and model evaluation metrics. Avoid retraining a large model during a live demonstration.
