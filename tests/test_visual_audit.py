import tempfile
import unittest
from pathlib import Path
from src.commerce_evolution_engine.visual_audit import valid_url, load_urls, signals, _safe_final_url


class VisualAuditTests(unittest.TestCase):
    def test_allows_public_products_only(self):
        good = "https://casaviva.company/producto/ventilador-recargable/"
        self.assertEqual(valid_url(good, {"casaviva.company"}), good)

    def test_rejects_sensitive_or_offsite_urls(self):
        bad = [
            "http://casaviva.company/producto/a/",
            "https://casaviva.company/wp-admin/",
            "https://casaviva.company/checkout/",
            "https://casaviva.company/producto/a/?key=secret",
            "https://evil.example/producto/a/",
            "https://casaviva.company.evil.example/producto/a/",
            "https://user:secret@casaviva.company/producto/a/",
            "https://casaviva.company:8443/producto/a/",
        ]
        for url in bad:
            with self.subTest(url=url), self.assertRaises(ValueError):
                valid_url(url, {"casaviva.company"})

    def test_reject_redirect_to_private_or_external_location(self):
        hosts = {"casaviva.company"}
        self.assertTrue(_safe_final_url("https://casaviva.company/producto/ejemplo/", hosts))
        self.assertFalse(_safe_final_url("https://casaviva.company/checkout/", hosts))
        self.assertFalse(_safe_final_url("https://externo.invalid/", hosts))

    def test_url_limit_and_deduplication(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "urls.txt"
            p.write_text("# comentario\nhttps://casaviva.company/\nhttps://casaviva.company/\n")
            self.assertEqual(load_urls(p, {"casaviva.company"}), ["https://casaviva.company/"])
            with self.assertRaises(ValueError):
                load_urls(p, {"casaviva.company"}, limit=0)

    def test_signals(self):
        sample = {"status": 200, "title": "", "h1": "", "h1_count": 0,
                  "overflow_px": 15, "broken_images": 1, "images_missing_alt": 2,
                  "main_text_chars": 12}
        issues = signals(sample)
        self.assertIn("sin_title", issues)
        self.assertIn("desbordamiento_horizontal", issues)
        self.assertIn("imagenes_sin_cargar", issues)


if __name__ == "__main__":
    unittest.main()
