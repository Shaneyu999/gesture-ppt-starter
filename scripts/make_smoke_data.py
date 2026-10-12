"""Generate simple hand-shaped PNGs for checking the training pipeline.

The images use only the Python standard library and are not meaningful for real
gesture-recognition evaluation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import random
import struct
import sys
import zlib


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

LABELS = ("palm", "peace", "thumbs_up", "fist")
COUNTS = {"train": 12, "val": 4}
COLORS = {
    "palm": (235, 196, 160),
    "peace": (220, 180, 150),
    "thumbs_up": (240, 205, 170),
    "fist": (205, 165, 135),
}


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def _write_png(path: Path, pixels: list[bytearray]) -> None:
    height = len(pixels)
    width = len(pixels[0]) // 3
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        raw.extend(row)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
        + _chunk(b"IEND", b"")
    )


def _set(pixels: list[bytearray], x: int, y: int, color: tuple[int, int, int]) -> None:
    height = len(pixels)
    width = len(pixels[0]) // 3
    if 0 <= x < width and 0 <= y < height:
        offset = x * 3
        pixels[y][offset : offset + 3] = bytes(color)


def _rect(pixels, x1, y1, x2, y2, color) -> None:
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            _set(pixels, x, y, color)


def _circle(pixels, center_x, center_y, radius, color) -> None:
    for y in range(center_y - radius, center_y + radius + 1):
        for x in range(center_x - radius, center_x + radius + 1):
            if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2:
                _set(pixels, x, y, color)


def _make_image(label: str, index: int, path: Path, seed: int) -> None:
    random.seed(f"{label}-{index}-{seed}")
    width = height = 128
    background = (235, 240, 245)
    pixels = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            noise = random.randint(-4, 4)
            row.extend(
                max(0, min(255, channel + noise))
                for channel in background
            )
        pixels.append(row)

    skin = COLORS[label]
    outline = (80, 50, 35)
    palm_x = 64 + random.randint(-4, 4)
    palm_y = 78 + random.randint(-4, 4)
    _circle(pixels, palm_x, palm_y, 25, skin)
    _circle(pixels, palm_x, palm_y, 27, outline)
    _circle(pixels, palm_x, palm_y, 25, skin)

    if label in ("palm", "peace"):
        fingers = [palm_x - 15, palm_x - 7, palm_x + 1, palm_x + 9, palm_x + 17]
        if label == "peace":
            fingers = [palm_x - 8, palm_x + 8]
        for finger_x in fingers:
            _rect(pixels, finger_x - 4, palm_y - 58, finger_x + 4, palm_y - 10, outline)
            _rect(pixels, finger_x - 2, palm_y - 56, finger_x + 2, palm_y - 12, skin)

    if label == "thumbs_up":
        _rect(pixels, palm_x + 20, palm_y - 55, palm_x + 31, palm_y - 10, outline)
        _rect(pixels, palm_x + 22, palm_y - 53, palm_x + 29, palm_y - 12, skin)

    _rect(pixels, palm_x - 30, palm_y + 22, palm_x + 30, palm_y + 34, outline)
    _write_png(path, pixels)


def make_smoke_dataset(output_dir: str | Path, seed: int = 42) -> Path:
    output = Path(output_dir)
    if not output.is_absolute():
        output = (PROJECT_ROOT / output).resolve()
    for split, count in COUNTS.items():
        for label in LABELS:
            for index in range(count):
                _make_image(
                    label,
                    index,
                    output / split / label / f"{label}_{index:04d}.png",
                    seed,
                )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic gesture images.")
    parser.add_argument("--output", default="data/smoke")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    output = make_smoke_dataset(args.output, args.seed)
    print(f"Smoke dataset created at {output}")
    print("Use it only to test code, not to report real accuracy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
