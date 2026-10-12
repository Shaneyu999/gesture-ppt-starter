"""Command-line interface for the gesture PPT starter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Sequence

from .actions import ActionMapper
from .camera import capture_images, run_camera_control
from .config import LabelConfig, default_label_config, load_actions
from .data import discover_samples
from .predictor import GesturePredictor, top3_text
from .stability import StableGestureGate
from .train import train_model


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gesture-ppt",
        description="Recognize hand gestures and control PowerPoint or video playback.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser(
        "capture",
        help="Collect gesture images from a webcam.",
    )
    capture.add_argument("--output", default="data/gestures/train")
    capture.add_argument("--label", required=True)
    capture.add_argument("--session", help="Name used in captured filenames.")
    capture.add_argument("--camera", type=int, default=0)
    capture.add_argument("--count", type=int, default=200)
    capture.add_argument("--interval", type=int, default=3)
    capture.add_argument("--labels", default="configs/labels.json")
    capture.set_defaults(handler=command_capture)

    train = subparsers.add_parser(
        "train",
        help="Train MobileNetV3-Small on captured gesture images.",
    )
    train.add_argument("--train-dir", default="data/gestures/train")
    train.add_argument("--val-dir", default="data/gestures/val")
    train.add_argument("--labels", default="configs/labels.json")
    train.add_argument("--output-dir", default="runs/gesture_model")
    train.add_argument("--epochs", type=int, default=12)
    train.add_argument("--batch-size", type=int, default=16)
    train.add_argument("--learning-rate", type=float, default=1e-3)
    train.add_argument("--weight-decay", type=float, default=1e-4)
    train.add_argument("--image-size", type=int, default=224)
    train.add_argument("--device")
    train.add_argument("--seed", type=int, default=42)
    train.add_argument("--freeze-backbone", action="store_true")
    train.add_argument("--class-weights", action="store_true")
    train.add_argument("--no-pretrained", action="store_true")
    train.set_defaults(handler=command_train)

    run = subparsers.add_parser(
        "run",
        help="Run real-time gesture preview and optional keyboard control.",
    )
    run.add_argument("--checkpoint", required=True)
    run.add_argument("--actions", default="configs/actions.json")
    run.add_argument("--camera", type=int, default=0)
    run.add_argument("--device")
    run.add_argument("--roi", type=float, default=0.65)
    run.add_argument("--predict-every", type=int, default=2)
    run.add_argument("--stable-frames", type=int, default=5)
    run.add_argument("--cooldown", type=float, default=1.5)
    run.add_argument("--min-confidence", type=float, default=0.60)
    run.add_argument(
        "--window-title",
        help="Optional window title to focus before sending a key.",
    )
    run.add_argument(
        "--enable-controls",
        action="store_true",
        help="Actually send keyboard keys. Preview only when omitted.",
    )
    run.set_defaults(handler=command_run)

    predict = subparsers.add_parser(
        "predict",
        help="Predict one image with a trained checkpoint.",
    )
    predict.add_argument("--image", required=True)
    predict.add_argument("--checkpoint", required=True)
    predict.add_argument("--device")
    predict.set_defaults(handler=command_predict)

    simulate = subparsers.add_parser(
        "simulate",
        help="Test stable-gesture and action logic without a camera.",
    )
    simulate.add_argument(
        "--sequence",
        default="palm,peace,thumbs_up,fist",
        help="Comma-separated gesture labels.",
    )
    simulate.add_argument("--actions", default="configs/actions.json")
    simulate.add_argument("--stable-frames", type=int, default=5)
    simulate.add_argument("--cooldown", type=float, default=1.5)
    simulate.add_argument("--min-confidence", type=float, default=0.60)
    simulate.add_argument("--enable-controls", action="store_true")
    simulate.set_defaults(handler=command_simulate)

    return parser


def _label_config(path: str | Path) -> LabelConfig:
    config_path = Path(path)
    return LabelConfig.from_json(config_path) if config_path.exists() else default_label_config()


def _print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_capture(args: argparse.Namespace) -> int:
    labels = _label_config(args.labels)
    if args.label not in labels.label_to_id:
        raise ValueError(
            f"Unknown label {args.label!r}; choose one of {list(labels.labels)}."
        )
    if args.count < 1:
        raise ValueError("--count must be at least 1.")
    if args.interval < 1:
        raise ValueError("--interval must be at least 1.")
    output = capture_images(
        args.output,
        args.label,
        camera_index=args.camera,
        count=args.count,
        interval=args.interval,
        session=args.session,
    )
    print(f"Images saved to {output}")
    return 0


def command_train(args: argparse.Namespace) -> int:
    labels = _label_config(args.labels)
    train_samples = discover_samples(args.train_dir, labels.labels)
    val_samples = discover_samples(args.val_dir, labels.labels)
    result = train_model(
        train_samples,
        val_samples,
        labels.labels,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        image_size=args.image_size,
        freeze_backbone=args.freeze_backbone,
        class_weights=args.class_weights,
        pretrained=not args.no_pretrained,
        device=args.device,
        seed=args.seed,
    )
    _print_json(result)
    return 0


def command_run(args: argparse.Namespace) -> int:
    predictor = GesturePredictor(args.checkpoint, device=args.device)
    actions = load_actions(args.actions)
    missing = sorted(set(predictor.labels) - set(actions))
    if missing:
        raise ValueError(f"Missing actions for gestures: {missing}")
    run_camera_control(
        predictor,
        actions,
        camera_index=args.camera,
        roi_fraction=args.roi,
        predict_every=args.predict_every,
        stable_frames=args.stable_frames,
        cooldown_seconds=args.cooldown,
        min_confidence=args.min_confidence,
        enable_controls=args.enable_controls,
        window_title=args.window_title,
    )
    return 0


def command_predict(args: argparse.Namespace) -> int:
    predictor = GesturePredictor(args.checkpoint, device=args.device)
    result = predictor.predict_file(args.image)
    _print_json(result)
    print(f"Top-3: {top3_text(result)}")
    return 0


def command_simulate(args: argparse.Namespace) -> int:
    actions = load_actions(args.actions)
    labels = [item.strip() for item in args.sequence.split(",") if item.strip()]
    if not labels:
        raise ValueError("--sequence must contain at least one gesture label.")

    mapper = ActionMapper(actions)
    gate = StableGestureGate(
        stable_frames=args.stable_frames,
        cooldown_seconds=args.cooldown,
        min_confidence=args.min_confidence,
    )
    now = 0.0
    triggered = 0
    for label in labels:
        for _ in range(args.stable_frames + 1):
            decision = gate.update(label, 0.95, now)
            now += 0.1
            if decision.triggered:
                event = mapper.perform(
                    label,
                    None,
                    enabled=args.enable_controls,
                )
                status = "EXECUTED" if event.executed else "PREVIEW"
                print(f"{status}: {label} -> {event.action} ({event.key})")
                triggered += 1
    print(f"Simulation completed with {triggered} triggered action(s).")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
