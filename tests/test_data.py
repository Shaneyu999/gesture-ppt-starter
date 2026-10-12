from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gesture_ppt.data import discover_samples, summarize_samples


class DataTests(unittest.TestCase):
    def test_discover_samples(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for label in ("palm", "peace"):
                class_dir = root / label
                class_dir.mkdir()
                (class_dir / "one.jpg").write_bytes(b"fake")
            samples = discover_samples(root, ["palm", "peace"])
            self.assertEqual(len(samples), 2)
            self.assertEqual(summarize_samples(samples), {"palm": 1, "peace": 1})

    def test_missing_class_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "palm").mkdir()
            (root / "palm" / "one.jpg").write_bytes(b"fake")
            with self.assertRaises(FileNotFoundError):
                discover_samples(root, ["palm", "peace"])


if __name__ == "__main__":
    unittest.main()
