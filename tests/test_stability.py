from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gesture_ppt.stability import StableGestureGate


class StabilityTests(unittest.TestCase):
    def test_gesture_triggers_after_stable_frames(self) -> None:
        gate = StableGestureGate(stable_frames=3, cooldown_seconds=1.0)
        self.assertFalse(gate.update("palm", 0.9, 0.0).triggered)
        self.assertFalse(gate.update("palm", 0.9, 0.1).triggered)
        self.assertTrue(gate.update("palm", 0.9, 0.2).triggered)

    def test_cooldown_blocks_repeated_trigger(self) -> None:
        gate = StableGestureGate(stable_frames=2, cooldown_seconds=1.0)
        gate.update("peace", 0.9, 0.0)
        self.assertTrue(gate.update("peace", 0.9, 0.1).triggered)
        gate.update("peace", 0.9, 0.2)
        self.assertFalse(gate.update("peace", 0.9, 0.3).triggered)

    def test_low_confidence_resets_candidate(self) -> None:
        gate = StableGestureGate(stable_frames=2, min_confidence=0.7)
        gate.update("fist", 0.9, 0.0)
        gate.update("fist", 0.3, 0.1)
        self.assertFalse(gate.update("fist", 0.9, 0.2).triggered)


if __name__ == "__main__":
    unittest.main()
