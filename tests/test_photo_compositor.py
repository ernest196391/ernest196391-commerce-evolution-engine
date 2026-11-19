import tempfile
import unittest
from pathlib import Path
from src.commerce_evolution_engine.photo_compositor import render_hero, render_benefits

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None


@unittest.skipIf(Image is None, "Pillow optional dependency not installed")
class PhotoCompositorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ref = self.root / "original-transparent.png"
        img = Image.new("RGBA", (150, 300), (0, 0, 0, 0))
        ImageDraw.Draw(img).rectangle((20, 10, 125, 290), fill=(20, 40, 100, 255))
        img.save(self.ref)
        self.original = self.ref.read_bytes()

    def test_hero_white_canvas_without_editing_source(self):
        out = self.root / "hero.png"
        result = render_hero(self.ref, out)
        self.assertTrue(result["requires_human_qa"])
        self.assertEqual(result["cost_usd_api"], 0)
        with Image.open(out) as img:
            self.assertEqual(img.size, (1200, 1200))
            self.assertEqual(img.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(self.original, self.ref.read_bytes())

    def test_benefits_limits_claims(self):
        facts = [{"label": "Autonomía anunciada", "value": "12 h", "evidence_id": "manual"}]
        out = self.root / "benefits.png"
        info = render_benefits(self.ref, out, headline="Ventilación cuando importa", facts=facts)
        self.assertEqual(info["facts"], 1)
        with self.assertRaises(ValueError):
            render_benefits(self.ref, out, headline="Datos", facts=[
                {"label": str(i), "value": "x", "evidence_id": "manual"} for i in range(3)])

    def test_no_original_overwrite(self):
        with self.assertRaises(ValueError):
            render_hero(self.ref, self.ref)
        self.assertEqual(self.original, self.ref.read_bytes())


if __name__ == "__main__":
    unittest.main()
