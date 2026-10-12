"""Train the gesture classifier."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from .data import GestureImageDataset, ImageSample, summarize_samples
from .metrics import summarize
from .model import build_model, build_transforms, resolve_device, save_checkpoint


def train_model(
    train_samples: Sequence[ImageSample],
    val_samples: Sequence[ImageSample],
    labels: Sequence[str],
    *,
    output_dir: str | Path,
    epochs: int = 12,
    batch_size: int = 16,
    learning_rate: float = 1e-3,
    weight_decay: float = 1e-4,
    image_size: int = 224,
    freeze_backbone: bool = False,
    class_weights: bool = False,
    pretrained: bool = True,
    device: str | None = None,
    seed: int = 42,
) -> dict[str, object]:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader

    torch.manual_seed(seed)
    runtime_device = resolve_device(device)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    train_dataset = GestureImageDataset(
        train_samples,
        transform=build_transforms(image_size, training=True),
    )
    val_dataset = GestureImageDataset(
        val_samples,
        transform=build_transforms(image_size, training=False),
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    model = build_model(
        len(labels),
        pretrained=pretrained,
        freeze_backbone=freeze_backbone,
    ).to(runtime_device)

    weights = None
    if class_weights:
        counts = torch.zeros(len(labels), dtype=torch.float32)
        for sample in train_samples:
            counts[sample.label_id] += 1
        safe_counts = counts.clamp_min(1)
        weights = counts.sum() / (len(labels) * safe_counts)
        weights = weights.to(runtime_device)

    criterion = nn.CrossEntropyLoss(weight=weights)
    parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = torch.optim.AdamW(
        parameters,
        lr=learning_rate,
        weight_decay=weight_decay,
    )

    best_state = None
    best_metrics: dict[str, object] | None = None
    best_accuracy = -1.0
    history: list[dict[str, float]] = []

    print(f"Training data: {summarize_samples(train_samples)}")
    print(f"Validation data: {summarize_samples(val_samples)}")

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for images, targets in train_loader:
            images = images.to(runtime_device)
            targets = targets.to(runtime_device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item()) * len(images)

        model.eval()
        truths: list[int] = []
        predictions: list[int] = []
        with torch.inference_mode():
            for images, targets in val_loader:
                logits = model(images.to(runtime_device))
                predicted = logits.argmax(dim=-1).cpu().tolist()
                predictions.extend(predicted)
                truths.extend(targets.tolist())

        metrics = summarize(truths, predictions, labels)
        metrics["train_loss"] = total_loss / max(1, len(train_samples))
        history.append(
            {
                "epoch": float(epoch),
                "train_loss": float(metrics["train_loss"]),
                "accuracy": float(metrics["accuracy"]),
                "macro_f1": float(metrics["macro_f1"]),
            }
        )
        print(
            f"epoch={epoch:03d} loss={metrics['train_loss']:.4f} "
            f"val_acc={metrics['accuracy']:.4f} val_f1={metrics['macro_f1']:.4f}"
        )

        if float(metrics["accuracy"]) > best_accuracy:
            best_accuracy = float(metrics["accuracy"])
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }
            best_metrics = metrics

    if best_state is None or best_metrics is None:
        raise RuntimeError("Training did not produce a valid checkpoint.")

    model.load_state_dict(best_state)
    checkpoint_path = output_path / "best.pt"
    save_checkpoint(
        checkpoint_path,
        model,
        labels,
        image_size=image_size,
        metrics=best_metrics,
    )
    (output_path / "metrics.json").write_text(
        json.dumps(
            {"best": best_metrics, "history": history},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "checkpoint": str(checkpoint_path),
        "metrics": best_metrics,
        "feature_dim": None,
    }
