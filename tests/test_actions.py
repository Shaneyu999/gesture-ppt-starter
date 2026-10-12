from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gesture_ppt.actions import ActionMapper
from gesture_ppt.config import ActionConfig


class FakeController:
    def __init__(self) -> None:
        self.keys: list[str] = []

    def press(self, key: str) -> None:
        self.keys.append(key)


class ActionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.actions = {
            "palm": ActionConfig("palm", "play_pause", "space"),
            "peace": ActionConfig("peace", "next", "right"),
        }
        self.mapper = ActionMapper(self.actions)

    def test_preview_does_not_send_key(self) -> None:
        controller = FakeController()
        event = self.mapper.perform("palm", controller, enabled=False)
        self.assertFalse(event.executed)
        self.assertEqual(controller.keys, [])

    def test_enabled_sends_configured_key(self) -> None:
        controller = FakeController()
        event = self.mapper.perform("peace", controller, enabled=True)
        self.assertTrue(event.executed)
        self.assertEqual(controller.keys, ["right"])


if __name__ == "__main__":
    unittest.main()
