from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gesture_ppt.metrics import accuracy, macro_f1


class MetricTests(unittest.TestCase):
    def test_accuracy(self) -> None:
        self.assertAlmostEqual(accuracy([0, 1, 1], [0, 1, 0]), 2 / 3)

    def test_macro_f1(self) -> None:
        self.assertAlmostEqual(macro_f1([0, 0, 1, 1], [0, 1, 1, 1]), 11 / 15)


if __name__ == "__main__":
    unittest.main()
