"""Gesture prediction from image files and webcam frames."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from .model import build_transforms, load_model


class GesturePredictor:
    def __init__(self, checkpoint_path: str | Path, device: str | None = None) -> None:
        self.model, self.labels, self.checkpoint, self.device = load_model(
            checkpoint_path,
            device=device,
        )
        self.image_size = int(self.checkpoint.get("image_size", 224))
        self.transform = build_transforms(self.image_size, training=False)

    def predict_pil(self, image: Any) -> dict[str, object]:
        import torch

        tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=-1)[0]
        predicted_id = int(probabilities.argmax().item())
        values = [float(value) for value in probabilities.cpu().tolist()]
        top_indices = sorted(
            range(len(values)),
            key=lambda index: values[index],
            reverse=True,
        )[:3]
        return {
            "label": self.labels[predicted_id],
            "label_id": predicted_id,
            "confidence": values[predicted_id],
            "probabilities": dict(zip(self.labels, values)),
            "top3": [
                {"label": self.labels[index], "confidence": values[index]}
                for index in top_indices
            ],
        }

    def predict_bgr(self, frame: Any) -> dict[str, object]:
        try:
            import cv2
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("opencv-python and Pillow are required.") from exc

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.predict_pil(Image.fromarray(rgb))

    def predict_file(self, image_path: str | Path) -> dict[str, object]:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required.") from exc

        with Image.open(image_path) as image:
            return self.predict_pil(image.convert("RGB"))


def top3_text(result: dict[str, object], display_names: dict[str, str] | None = None) -> str:
    names = display_names or {}
    parts = []
    for item in result["top3"]:
        label = str(item["label"])
        parts.append(f"{names.get(label, label)} {float(item['confidence']):.2f}")
    return " | ".join(parts)
