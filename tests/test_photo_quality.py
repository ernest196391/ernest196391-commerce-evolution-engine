import tempfile
import unittest
from pathlib import Path
from src.commerce_evolution_engine.photo_quality import inspect

try:
    from PIL import Image
except ImportError:
    Image = None


@unittest.skipIf(Image is None, "Pillow optional; install to run image QA tests")
class PhotoQualityTests(unittest.TestCase):
    def test_missing_slots_never_pass(self):
        with tempfile.TemporaryDirectory() as t:
            r = inspect(Path(t))
            self.assertFalse(r["technical_ready"])
            self.assertTrue(r["human_approval_required"])
            self.assertEqual(sum(x["status"]=="missing" for x in r["slots"]), 3)

    def test_all_four_distinct_and_correct_formats(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            for i, filename in enumerate(("01-hero.png", "02-lifestyle.png", "03-benefits.png", "04-details.png")):
                size = (900, 900) if i == 0 else (800, 1000)
                Image.new("RGB", size, (255, 255, 255) if i == 0 else (20*i, 80, 100)).save(base / filename)
            result = inspect(base)
            self.assertTrue(result["technical_ready"])

    def test_three_pass_but_missing_required_fourth_fails(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            for i, filename in enumerate(("01-hero.png", "02-lifestyle.png", "03-benefits.png")):
                Image.new("RGB", (900, 900) if i == 0 else (800, 1000), (255,255,255) if i == 0 else (20*i,80,100)).save(base / filename)
            self.assertTrue(inspect(base)["technical_ready"])
            self.assertFalse(inspect(base, require_details=True)["technical_ready"])

    def test_duplicate_images_are_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            img = Image.new("RGB", (800, 1000), (40, 70, 80))
            img.save(base / "02-lifestyle.png")
            img.save(base / "03-benefits.png")
            result = inspect(base)
            self.assertTrue(any("contenido_binario_duplicado" in slot["issues"] for slot in result["slots"]))


if __name__ == "__main__":
    unittest.main()
