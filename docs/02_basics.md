# Technical Background

This document explains the main concepts behind the gesture recognition and real-time control project.

## 1. Image Classification

Image classification takes an image as input and returns a class label:

~~~text
Image -> Model -> palm / peace / thumbs_up / fist
~~~

The model converts the image into numerical features and estimates the probability of each class.

## 2. Webcam Frames

A video is a sequence of images ordered in time:

~~~text
Frame 1 -> Frame 2 -> Frame 3 -> ...
~~~

OpenCV reads camera frames through VideoCapture. Each frame is normally a NumPy array in BGR order.

The project classifies only the center region because the hand is usually placed there and the surrounding background is less likely to dominate the prediction.

## 3. Center-Region Cropping

When the full frame is classified, the model may learn irrelevant patterns such as:

- Tables;
- Walls;
- Human bodies;
- Monitors;
- Fixed lighting.

Center cropping increases the relative area of the hand and improves stability. The option --roi 0.65 means that the crop size is 65 percent of the shorter image dimension.

## 4. Tensors

A common PyTorch image input shape is:

~~~text
[N, C, H, W]
~~~

- N: batch size;
- C: number of color channels, normally 3 for RGB;
- H: height;
- W: width.

The model input is normally resized to 224 by 224 pixels.

## 5. Training, Validation, and Test Sets

- Training set: updates model parameters;
- Validation set: selects the best model;
- Test set: used once for the final evaluation.

The main risk in gesture datasets is data leakage. If training and validation sets contain adjacent frames from the same recording, the frames are nearly identical and validation accuracy becomes unrealistically high.

Separate sessions, backgrounds, or participants should be used for validation.

## 6. Data Augmentation

Common augmentations include:

- Random cropping;
- Random horizontal flipping;
- Brightness changes;
- Contrast changes;
- Saturation changes;
- Small hue changes.

Augmentation simulates different environments and hand positions. Horizontal flipping may change the meaning of directional gestures and should be used according to the gesture definition.

## 7. Transfer Learning

Training an image model from scratch requires a large dataset. Transfer learning starts from an ImageNet-pretrained model and replaces the output layer for the target classes.

This project:

1. Loads MobileNetV3-Small;
2. Keeps the pretrained feature extractor;
3. Replaces the final classifier with four outputs;
4. Trains on a relatively small gesture dataset.

When data is limited, the backbone can be frozen with:

~~~powershell
--freeze-backbone
~~~

After collecting more data, the full model can be fine-tuned.

## 8. MobileNetV3

MobileNetV3 is a lightweight convolutional network designed for mobile and edge devices.

Advantages:

- Small parameter count;
- Fast inference;
- Suitable for CPU execution;
- Appropriate for real-time demonstration.

Limitations:

- Lower representational capacity than large models;
- Less stable under complex backgrounds;
- Requires well-controlled training data.

## 9. Classification Output and Probability

The model produces logits. A Softmax operation converts them into class probabilities:

~~~text
palm       0.08
peace      0.91
thumbs_up  0.01
fist       0.00
~~~

The class with the highest probability is selected by default. A confidence threshold rejects uncertain predictions.

## 10. Why Every Frame Must Not Send a Key

A real-time video pipeline can process dozens of frames per second. If the model recognizes a peace sign 20 times in one second and sends the right-arrow key each time, the presentation may advance by many slides.

The system therefore uses:

### Stable Frames

The same gesture must appear for several consecutive frames.

### Cooldown

After an action is executed, the same action is blocked for a fixed period such as 1.5 seconds.

### Confidence

Predictions below a threshold such as 0.60 do not participate in action triggering.

## 11. State-Machine Logic

The project uses a simplified state machine:

~~~text
No candidate gesture
  -> peace is observed repeatedly
  -> counter increases
  -> stable-frame threshold is reached
  -> cooldown is checked
  -> next action is triggered
  -> counter is reset
~~~

If the predicted gesture changes, the candidate gesture and counter are restarted.

## 12. Keyboard Control

The pyautogui library can send a key to the currently active window. For example, pyautogui.press("right") sends the right-arrow key.

This design has several implications:

- PowerPoint or the media player should be in the foreground;
- If the camera window has focus, the key may not reach the presentation;
- Important software should not be controlled without supervision;
- Preview mode is safer by default.

## 13. Keyboard Control versus PowerPoint API

Keyboard control is:

- Compatible with PowerPoint, media players, and browsers;
- Simple to implement;
- Independent of Office plug-ins;
- Suitable for rapid demonstration.

Its limitations are:

- It depends on the active foreground window;
- Key mappings may differ between applications;
- It cannot read the current slide number or playback state.

## 14. Model Checkpoints

Training produces:

~~~text
runs/gesture_model/best.pt
~~~

The checkpoint contains:

- Model parameters;
- Class order;
- Input image size;
- Best validation metrics.

The inference pipeline must preserve the same class order. The labels are therefore loaded directly from the checkpoint.

## 15. Evaluation Metrics

### Accuracy

The proportion of correct predictions.

### Macro F1

The average F1 score across classes. It is useful for detecting whether a minority gesture class is being ignored.

### Per-Class Recall

The proportion of examples from a given gesture class that are correctly recognized.

### Confusion Matrix

A table that shows which gestures are confused with one another, for example:

- Peace sign and open palm;
- Fist and thumbs up;
- Open palm and background.

### FPS

Frames processed per second. Real-time demonstrations often target at least 15 FPS.

## 16. Common Data Problems

- Backgrounds are too repetitive;
- Training and validation frames come from the same session;
- Gesture classes are imbalanced;
- The hand is too far from the camera;
- Images are blurred;
- Consecutive frames are nearly identical;
- Left and right hands are not both represented.

## 17. Common Training Problems

### Validation Accuracy Does Not Improve

- Increase the dataset;
- Freeze the backbone first;
- Check for incorrect labels;
- Adjust the learning rate;
- Check class balance.

### High Training Accuracy but Low Validation Accuracy

- Possible data leakage;
- Background overfitting;
- Too little data;
- Insufficient augmentation;
- Different distributions between training and validation sets.

### Unstable Real-Time Predictions

- Increase the number of stable frames;
- Add difficult examples;
- Adjust the ROI;
- Improve lighting;
- Do not rely on a single-frame prediction.

## 18. Recommended Code Reading Order

1. config.py: label and action configuration;
2. data.py: folder-based image loading;
3. model.py: MobileNetV3 and image transforms;
4. train.py: training loop;
5. predictor.py: single-image and camera inference;
6. stability.py: stable frames and cooldown;
7. actions.py: action mapping and keyboard control;
8. camera.py: image capture and real-time window;
9. cli.py: command-line entry points.

## 19. Minimal Learning Path

1. Python fundamentals;
2. NumPy and image loading;
3. PyTorch Dataset and DataLoader;
4. Transfer learning;
5. OpenCV camera input;
6. State machines and debouncing;
7. Desktop automation;
8. Training, preview, and controlled demonstration.
