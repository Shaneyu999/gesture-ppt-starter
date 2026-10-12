"""Label and action configuration."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Mapping


DEFAULT_LABELS = ("palm", "peace", "thumbs_up", "fist")

DEFAULT_DISPLAY_NAMES_ZH = {
    "palm": "张开手掌",
    "peace": "剪刀手",
    "thumbs_up": "点赞",
    "fist": "握拳",
}


@dataclass(frozen=True)
class LabelConfig:
    labels: tuple[str, ...]
    display_names_zh: Mapping[str, str]

    def __post_init__(self) -> None:
        if not self.labels:
            raise ValueError("At least one label is required.")
        if len(set(self.labels)) != len(self.labels):
            raise ValueError("Labels must be unique.")

    @property
    def label_to_id(self) -> dict[str, int]:
        return {label: index for index, label in enumerate(self.labels)}

    @property
    def id_to_label(self) -> dict[int, str]:
        return {index: label for index, label in enumerate(self.labels)}

    @classmethod
    def from_json(cls, path: str | Path) -> "LabelConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            labels=tuple(str(label) for label in data.get("labels", DEFAULT_LABELS)),
            display_names_zh=dict(
                data.get("display_names_zh", DEFAULT_DISPLAY_NAMES_ZH)
            ),
        )


def default_label_config() -> LabelConfig:
    return LabelConfig(DEFAULT_LABELS, DEFAULT_DISPLAY_NAMES_ZH)


@dataclass(frozen=True)
class ActionConfig:
    label: str
    action: str
    key: str
    description: str = ""


def load_actions(path: str | Path) -> dict[str, ActionConfig]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Actions JSON must be an object.")
    actions: dict[str, ActionConfig] = {}
    for label, value in data.items():
        if not isinstance(value, dict):
            raise ValueError(f"Action entry for {label!r} must be an object.")
        action = str(value.get("action", "")).strip()
        key = str(value.get("key", "")).strip()
        if not action or not key:
            raise ValueError(f"Action entry for {label!r} needs action and key.")
        actions[str(label)] = ActionConfig(
            label=str(label),
            action=action,
            key=key,
            description=str(value.get("description", "")),
        )
    return actions
