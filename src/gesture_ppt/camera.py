"""Webcam capture and real-time gesture control."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import time
from typing import Mapping

from .actions import ActionMapper, KeyboardController
from .config import ActionConfig
from .stability import StableGestureGate


def require_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "opencv-python is required. Install dependencies with "
            "`pip install -e .`."
        ) from exc
    return cv2


def open_camera(camera_index: int):
    cv2 = require_cv2()
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"Could not open camera index {camera_index}.")
    return capture


def center_crop_bgr(frame, fraction: float):
    if not 0.1 <= fraction <= 1.0:
        raise ValueError("ROI fraction must be between 0.1 and 1.0.")
    height, width = frame.shape[:2]
    size = int(min(height, width) * fraction)
    x1 = max(0, (width - size) // 2)
    y1 = max(0, (height - size) // 2)
    x2 = min(width, x1 + size)
    y2 = min(height, y1 + size)
    return frame[y1:y2, x1:x2], (x1, y1, x2, y2)


def capture_images(
    output_dir: str | Path,
    label: str,
    *,
    camera_index: int = 0,
    count: int = 200,
    interval: int = 3,
    session: str | None = None,
) -> Path:
    cv2 = require_cv2()
    output = Path(output_dir) / label
    output.mkdir(parents=True, exist_ok=True)
    session_id = session or datetime.now().strftime("%Y%m%d-%H%M%S")
    capture = open_camera(camera_index)
    recording = False
    frame_index = 0
    saved = 0
    print("Press SPACE to start/stop, Q or ESC to quit.")
    print(f"Saving gesture {label!r} to {output}")

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("Failed to read a camera frame.")
            frame_index += 1

            if recording and saved < count and frame_index % interval == 0:
                filename = f"{label}_{session_id}_{saved:05d}.jpg"
                image_path = output / filename
                if not cv2.imwrite(str(image_path), frame):
                    raise RuntimeError(f"Could not write image: {image_path}")
                saved += 1

            status = "RECORDING" if recording else "PAUSED"
            color = (0, 0, 255) if recording else (0, 200, 0)
            cv2.putText(
                frame,
                f"{status} {saved}/{count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                color,
                2,
            )
            cv2.putText(
                frame,
                f"label={label}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )
            cv2.imshow("Gesture Capture", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord(" "):
                recording = not recording
            if saved >= count and recording:
                recording = False
                print(f"Captured {saved} images.")
    finally:
        capture.release()
        cv2.destroyAllWindows()
    return output


def _draw_run_overlay(
    cv2,
    frame,
    *,
    result: dict[str, object],
    roi_box: tuple[int, int, int, int],
    action_text: str,
    controls_enabled: bool,
    fps: float,
    stable_frames: int,
) -> None:
    x1, y1, x2, y2 = roi_box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 220, 80), 2)

    label = str(result.get("label", ""))
    confidence = float(result.get("confidence", 0.0))
    lines = [
        f"Gesture: {label} {confidence:.2f}",
        f"Action: {action_text}",
        f"Controls: {'ON' if controls_enabled else 'PREVIEW ONLY'}",
        f"Stable: {stable_frames}",
        f"FPS: {fps:.1f}",
    ]
    y = 28
    for line in lines:
        cv2.putText(
            frame,
            line,
            (18, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (255, 255, 255),
            2,
        )
        y += 28


def run_camera_control(
    predictor,
    actions: Mapping[str, ActionConfig],
    *,
    camera_index: int = 0,
    roi_fraction: float = 0.65,
    predict_every: int = 2,
    stable_frames: int = 5,
    cooldown_seconds: float = 1.5,
    min_confidence: float = 0.60,
    enable_controls: bool = False,
    window_title: str | None = None,
) -> None:
    cv2 = require_cv2()
    capture = open_camera(camera_index)
    mapper = ActionMapper(actions)
    controller = KeyboardController(window_title) if enable_controls else None
    gate = StableGestureGate(
        stable_frames=stable_frames,
        cooldown_seconds=cooldown_seconds,
        min_confidence=min_confidence,
    )

    frame_index = 0
    last_result: dict[str, object] = {
        "label": "",
        "confidence": 0.0,
        "top3": [],
    }
    last_time = time.perf_counter()
    fps = 0.0
    last_action_text = "none"

    print("Real-time preview started.")
    print("Press Q or ESC to quit.")
    if enable_controls:
        print("Keyboard control is ENABLED. Focus the target window after starting.")
    else:
        print("Preview only. Add --enable-controls to send keyboard keys.")

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("Failed to read a camera frame.")
            frame_index += 1

            roi, roi_box = center_crop_bgr(frame, roi_fraction)
            if frame_index % max(1, predict_every) == 0:
                last_result = predictor.predict_bgr(roi)

            now = time.perf_counter()
            dt = now - last_time
            last_time = now
            if dt > 0:
                instant_fps = 1.0 / dt
                fps = instant_fps if fps == 0 else 0.9 * fps + 0.1 * instant_fps

            label = str(last_result.get("label", ""))
            confidence = float(last_result.get("confidence", 0.0))
            stable_count = 0
            if label:
                decision = gate.update(label, confidence, now)
                stable_count = decision.stable_frames
                if decision.triggered:
                    event = mapper.perform(
                        label,
                        controller,
                        enabled=enable_controls,
                    )
                    last_action_text = (
                        f"{event.description} ({event.key})"
                        if event.description
                        else f"{event.action} ({event.key})"
                    )
                    status = "EXECUTED" if event.executed else "PREVIEW"
                    print(f"{status}: {label} -> {last_action_text}")

            _draw_run_overlay(
                cv2,
                frame,
                result=last_result,
                roi_box=roi_box,
                action_text=last_action_text,
                controls_enabled=enable_controls,
                fps=fps,
                stable_frames=stable_count,
            )
            cv2.imshow("Gesture PPT Control", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()
