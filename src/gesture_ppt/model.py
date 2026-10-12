"""MobileNetV3 model construction and inference helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence


def resolve_device(requested: str | None = None) -> Any:
    import torch

    if requested:
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def build_model(
    num_classes: int,
    *,
    pretrained: bool = True,
    freeze_backbone: bool = False,
) -> Any:
    """Build MobileNetV3-Small and replace its classifier head."""

    try:
        from torch import nn
        from torchvision.models import MobileNet_V3_Small_Weights
        from torchvision.models import mobilenet_v3_small
    except ImportError as exc:
        raise RuntimeError(
            "torchvision is required. Install dependencies with `pip install -e .`."
        ) from exc

    weights = MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
    model = mobilenet_v3_small(weights=weights)
    if freeze_backbone:
        for parameter in model.features.parameters():
            parameter.requires_grad = False

    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    return model


def build_transforms(image_size: int = 224, training: bool = False):
    try:
        from torchvision import transforms
    except ImportError as exc:
        raise RuntimeError(
            "torchvision is required. Install dependencies with `pip install -e .`."
        ) from exc

    normalize = transforms.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225),
    )
    if training:
        return transforms.Compose(
            [
                transforms.Resize((256, 256)),
                transforms.RandomResizedCrop(image_size, scale=(0.70, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(
                    brightness=0.25,
                    contrast=0.25,
                    saturation=0.20,
                    hue=0.04,
                ),
                transforms.ToTensor(),
                normalize,
            ]
        )
    return transforms.Compose(
        [
            transforms.Resize((256, 256)),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            normalize,
        ]
    )


def save_checkpoint(
    path: str | Path,
    model: Any,
    labels: Sequence[str],
    *,
    image_size: int,
    metrics: dict[str, object],
) -> None:
    import torch

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "architecture": "mobilenet_v3_small",
            "model_state": {
                key: value.detach().cpu()
                for key, value in model.state_dict().items()
            },
            "labels": list(labels),
            "image_size": image_size,
            "metrics": metrics,
        },
        output,
    )


def load_model(checkpoint_path: str | Path, device: str | None = None):
    import torch

    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    labels = [str(label) for label in checkpoint["labels"]]
    model = build_model(len(labels), pretrained=False)
    model.load_state_dict(checkpoint["model_state"])
    runtime_device = resolve_device(device)
    model.to(runtime_device)
    model.eval()
    return model, labels, checkpoint, runtime_device
