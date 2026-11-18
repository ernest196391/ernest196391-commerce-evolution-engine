import csv
import tempfile
import unittest
from pathlib import Path
from src.commerce_evolution_engine.audit import audit, analyze, plain


class AuditTests(unittest.TestCase):
    def test_generic_title_and_missing_fields(self):
        result = audit({"id": "1", "name": "Producto", "description": "", "short_description": "", "images": ""})
        self.assertLess(result["score"], 60)
        self.assertIn("titulo_generico", result["findings"])
        self.assertIn("sin_imagen_referenciada", result["findings"])

    def test_four_images_can_be_counted_without_quality_claim(self):
        result = audit({"name": "Conectores solares MC4 juego", "description": "Esta es una descripción de más de cien caracteres y sin características inventadas. Los valores técnicos quedan sujetos a confirmación.", "short_description": "Juego de conectores técnicos por confirmar", "images": "a|b|c|d"})
        self.assertEqual(result["image_references"], 4)
        self.assertNotIn("menos_de_cuatro_imagenes_referenciadas", result["findings"])

    def test_strips_html(self):
        self.assertEqual(plain("<p>Producto &amp; accesorios</p>"), "Producto & accesorios")

    def test_csv_woo_headers_and_sort(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["ID", "Name", "Description", "Short description", "Images"])
                w.writeheader()
                w.writerow({"ID": "7", "Name": "Producto", "Description": "", "Short description": "", "Images": ""})
                w.writerow({"ID": "8", "Name": "Juegos de montaje para instalaciones solares", "Description": "Detalle largo con especificaciones por comprobar. " * 4, "Short description": "Conjunto en espera de validación del proveedor", "Images": "a,b,c,d"})
            result = analyze(path)
            self.assertEqual(result["input_rows"], 2)
            self.assertEqual(result["products"][0]["id"], "7")
            self.assertEqual(result["products"][1]["image_references"], 4)


if __name__ == "__main__":
    unittest.main()
