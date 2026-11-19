import tempfile
import unittest
from pathlib import Path

from src.commerce_evolution_engine.photo_compositor import render_benefits

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None


@unittest.skipIf(Image is None, 'Pillow not installed')
class CompositionLayoutTests(unittest.TestCase):
    def test_readable_layout_and_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'source.png'
            out = Path(tmp) / 'output.png'
            img = Image.new('RGBA', (400, 700))
            ImageDraw.Draw(img).rectangle((100, 50, 300, 650), fill='red')
            img.save(src)
            facts = [{'label':'Entrada USB','value':'5 V / 1 A','evidence_id':'label'}]
            render_benefits(src, out, headline='Recarga USB', facts=facts)
            with Image.open(out) as result:
                self.assertEqual(result.size, (1080, 1350))
                self.assertEqual(result.getpixel((1079, 75)), (248,248,246))
            before = out.read_bytes()
            for headline, bad_facts, kwargs in [
                ('W'*52, facts, {}),
                ('USB', facts, {'width':800,'height':1000}),
                ('USB', [{'label':'Carga\nUSB','value':'5 V','evidence_id':'label'}], {}),
            ]:
                with self.subTest(headline=headline), self.assertRaises(ValueError):
                    render_benefits(src, out, headline=headline, facts=bad_facts, **kwargs)
                self.assertEqual(out.read_bytes(), before)
