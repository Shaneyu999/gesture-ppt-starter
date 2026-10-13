# Project Introduction and Research Method

## 1. Project Title

**A Lightweight Vision System for Real-Time Gesture-Based Human-Computer Interaction**

Demonstration scenario: a normal webcam recognizes four hand gestures and controls PowerPoint or a video player.

## 2. Research Background

Presentations and video playback usually depend on a mouse, keyboard, or remote control. Camera-based gesture interaction reduces hardware dependence and can support touch-free presentations, public displays, and assistive interaction.

Compared with age-group recognition, gesture recognition provides clearer visual cues:

- Number of visible fingers;
- Hand contour;
- Thumb direction;
- Relationship between the hand and body;
- Changes across consecutive frames.

It is therefore a suitable entry point for studying image classification and real-time human-computer interaction.

## 3. Research Task

The input is a webcam frame. The output is one of four gesture classes:

| Label | Gesture | Default Action |
| --- | --- | --- |
| palm | Open palm | Play or pause |
| peace | Peace sign | Next slide or forward |
| thumbs_up | Thumbs up | Previous slide or rewind |
| fist | Closed fist | Mute |

The system then maps the recognized gesture to a keyboard action.

## 4. System Architecture

~~~text
Camera
  -> Center-region crop
  -> MobileNetV3-Small classification
  -> Confidence filtering
  -> Stable-frame check
  -> Cooldown control
  -> Keyboard action mapping
  -> PowerPoint or video player
~~~

## 5. Model Selection

The project uses MobileNetV3-Small:

- Small parameter count;
- Fast CPU inference;
- Suitable for transfer learning from ImageNet;
- The final classification layer can be replaced for four gesture classes.

Training options include:

- Freezing the backbone and training only the classifier;
- Fine-tuning the full model;
- Class-weighted loss;
- Data augmentation.

## 6. Data Collection

A practical target is 100 to 300 images per gesture. Training and validation data should come from different sessions.

The dataset should cover:

- Different backgrounds;
- Different lighting conditions;
- Left and right hands;
- Different hand-to-camera distances;
- Different gesture orientations;
- Different participants and camera positions.

Consecutive frames from one recording must not be randomly divided between training and validation. Such a split causes data leakage and inflates validation accuracy.

## 7. False-Trigger Prevention

If the model sends a key on every frame, a single gesture can create many repeated actions. Three constraints are used:

1. **Confidence threshold**: low-confidence predictions do not trigger an action;
2. **Stable frames**: the same gesture must persist for several consecutive frames;
3. **Cooldown**: the same action cannot be repeated within a short time window.

This logic is implemented in stability.py and can be tested without a camera.

## 8. Keyboard Control Design

Action mappings are stored in configs/actions.json:

~~~json
{
  "palm": { "action": "play_pause", "key": "space" },
  "peace": { "action": "next", "key": "right" },
  "thumbs_up": { "action": "previous", "key": "left" },
  "fist": { "action": "mute", "key": "m" }
}
~~~

Keyboard events are sent only when the --enable-controls option is explicitly provided. The default mode is preview only, which reduces the risk of unintended actions in the foreground window.

## 9. Experimental Design

### Experiment 1: Classification Baseline

Compare a frozen backbone with full fine-tuning using accuracy, Macro F1, training time, and model size.

### Experiment 2: Data Augmentation

Compare no augmentation, random cropping, color perturbation, and horizontal flipping.

### Experiment 3: Background Influence

Collect data under different backgrounds and test whether the model depends on a fixed background.

### Experiment 4: Lighting and Distance

Test low light, backlighting, changes in hand distance, and partial occlusion.

### Experiment 5: False-Trigger Parameters

Compare stable-frame counts, confidence thresholds, and cooldown periods using:

- Number of false triggers;
- Number of missed triggers;
- Average response time;
- Success rate for consecutive actions.

### Experiment 6: Real-Time Performance

Measure:

- Inference time per frame;
- FPS;
- CPU usage;
- Difference between GPU and CPU inference;
- Speed after ONNX export.

## 10. Evaluation Metrics

Classification metrics:

- Accuracy;
- Macro F1;
- Per-class recall;
- Confusion matrix.

Interaction metrics:

- Number of false triggers;
- Number of missed triggers;
- Delay from gesture appearance to action execution;
- Success rate during continuous presentation control;
- Real-time FPS.

## 11. Expected Outcomes

- A trainable four-class gesture classifier;
- A real-time webcam demonstration;
- A gesture-to-key mapping for PowerPoint and video playback;
- A stability and cooldown mechanism for preventing false triggers;
- Experimental analysis of background, lighting, distance, and real-time performance;
- A complete project suitable for release on GitHub.

## 12. Future Extensions

1. Use hand landmarks as additional classification features;
2. Apply temporal models to dynamic gestures such as waving or drawing circles;
3. Support gesture combinations and password-like interaction;
4. Add a touch-free mouse interface;
5. Deploy with ONNX Runtime or TensorRT;
6. Study personal adaptation across different users.
