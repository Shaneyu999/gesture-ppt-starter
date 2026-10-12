"""Check whether OpenCV can open a webcam."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gesture_ppt.camera import open_camera, require_cv2


def main() -> int:
    parser = argparse.ArgumentParser(description="Check webcam access.")
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    cv2 = require_cv2()
    capture = open_camera(args.camera)
    print(f"OpenCV {cv2.__version__}")
    print("Camera opened. Press Q or ESC to close.")
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("Failed to read a camera frame.")
            cv2.putText(
                frame,
                "Camera OK - press Q to quit",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            cv2.imshow("Camera Check", frame)
            if (cv2.waitKey(1) & 0xFF) in (ord("q"), 27):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

