"""Map gestures to safe keyboard actions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .config import ActionConfig


class KeyboardController:
    """Send keyboard keys through pyautogui when explicitly enabled."""

    def __init__(self, window_title: str | None = None) -> None:
        try:
            import pyautogui
        except ImportError as exc:
            raise RuntimeError(
                "Enable controls requires pyautogui. Install dependencies with "
                "`pip install -e .`."
            ) from exc
        self._pyautogui = pyautogui
        self._pyautogui.FAILSAFE = True
        self.window_title = window_title

    def _focus_target_window(self) -> None:
        if not self.window_title:
            return
        if not hasattr(self._pyautogui, "getWindowsWithTitle"):
            raise RuntimeError(
                "--window-title is not supported by this pyautogui backend. "
                "Omit it and keep the target window focused manually."
            )
        windows = self._pyautogui.getWindowsWithTitle(self.window_title)
        if not windows:
            raise RuntimeError(
                f"No window title matched {self.window_title!r}. "
                "Open the target slide show or video first."
            )
        window = windows[0]
        if hasattr(window, "isActive") and not window.isActive:
            window.activate()
            import time

            time.sleep(0.08)

    def press(self, key: str) -> None:
        self._focus_target_window()
        self._pyautogui.press(key)


@dataclass
class ActionEvent:
    label: str
    action: str
    key: str
    description: str
    executed: bool


class ActionMapper:
    def __init__(self, actions: Mapping[str, ActionConfig]) -> None:
        self.actions = dict(actions)

    def resolve(self, label: str) -> ActionConfig:
        try:
            return self.actions[label]
        except KeyError as exc:
            raise KeyError(f"No action is configured for gesture {label!r}.") from exc

    def perform(
        self,
        label: str,
        controller: KeyboardController | None,
        *,
        enabled: bool,
    ) -> ActionEvent:
        config = self.resolve(label)
        executed = False
        if enabled:
            if controller is None:
                controller = KeyboardController()
            controller.press(config.key)
            executed = True
        return ActionEvent(
            label=label,
            action=config.action,
            key=config.key,
            description=config.description,
            executed=executed,
        )

