"""Folder-based gesture image loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class ImageSample:
    path: Path
    label: str
    label_id: int


def discover_samples(root: str | Path, labels: Sequence[str]) -> list[ImageSample]:
    dataset_root = Path(root)
    if not dataset_root.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_root}")

    samples: list[ImageSample] = []
    for label_id, label in enumerate(labels):
        class_dir = dataset_root / label
        if not class_dir.is_dir():
            raise FileNotFoundError(f"Missing class directory: {class_dir}")
        class_images = sorted(
            path
            for path in class_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )
        if not class_images:
            raise ValueError(f"No images found in {class_dir}")
        samples.extend(
            ImageSample(path=path, label=label, label_id=label_id)
            for path in class_images
        )
    return samples


def summarize_samples(samples: Sequence[ImageSample]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sample in samples:
        counts[sample.label] = counts.get(sample.label, 0) + 1
    return counts


class GestureImageDataset:
    """PIL-image dataset compatible with torch.utils.data.DataLoader."""

    def __init__(self, samples: Sequence[ImageSample], transform=None) -> None:
        self.samples = list(samples)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required. Run `pip install -e .`.") from exc

        sample = self.samples[index]
        with Image.open(sample.path) as image:
            rgb_image = image.convert("RGB")
        if self.transform is not None:
            rgb_image = self.transform(rgb_image)
        return rgb_image, sample.label_id
