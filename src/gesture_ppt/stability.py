"""Debounce repeated gesture predictions before sending keyboard actions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GestureDecision:
    label: str
    triggered: bool
    stable_frames: int
    confidence: float


class StableGestureGate:
    """Require a gesture to persist before triggering an action."""

    def __init__(
        self,
        stable_frames: int = 5,
        cooldown_seconds: float = 1.5,
        min_confidence: float = 0.60,
    ) -> None:
        if stable_frames < 1:
            raise ValueError("stable_frames must be at least 1.")
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must not be negative.")
        if not 0 <= min_confidence <= 1:
            raise ValueError("min_confidence must be between 0 and 1.")
        self.stable_frames = stable_frames
        self.cooldown_seconds = cooldown_seconds
        self.min_confidence = min_confidence
        self._candidate = ""
        self._count = 0
        self._last_trigger_time: dict[str, float] = {}

    def reset(self) -> None:
        self._candidate = ""
        self._count = 0

    def update(self, label: str, confidence: float, now: float) -> GestureDecision:
        if confidence < self.min_confidence:
            self.reset()
            return GestureDecision("", False, 0, confidence)

        if label == self._candidate:
            self._count += 1
        else:
            self._candidate = label
            self._count = 1

        previous = self._last_trigger_time.get(label)
        cooldown_ready = (
            previous is None or now - previous >= self.cooldown_seconds
        )
        triggered = self._count >= self.stable_frames and cooldown_ready
        if triggered:
            self._last_trigger_time[label] = now
            self._count = 0

        return GestureDecision(
            label=label,
            triggered=triggered,
            stable_frames=self._count,
            confidence=confidence,
        )
