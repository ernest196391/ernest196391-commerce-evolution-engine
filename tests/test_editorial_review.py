import csv
import tempfile
import unittest
from pathlib import Path
from src.commerce_evolution_engine.editorial_review import triage, analyze


class EditorialReviewTests(unittest.TestCase):
    def test_filled_but_bad_description_is_flagged(self):
        row = {"id": "1", "name": "Ventilador", "description": "Excelente calidad. Ideal para todo.", "short_description": "Ventilador", "images": "uno.jpg"}
        result = triage(row)
        self.assertIn("descripcion_no_suficiente_para_decidir", result["flags"])
        self.assertIn("lenguaje_generico_promocional", result["flags"])
        self.assertLess(result["editorial_score"], 80)

    def test_claim_requires_source_not_automatic_rejection(self):
        row = {"id": "2", "name": "Ventilador portátil modelo de muestra", "description": "El proveedor anuncia hasta 20 horas de autonomía con batería de 8000 mAh. Confirmar condiciones de uso, velocidad de ventilación, inclusión de luz y voltaje según el documento técnico del fabricante.", "short_description": "Modelo portátil con autonomía anunciada pendiente de verificar", "images": "a.jpg|b.jpg|c.jpg|d.jpg"}
        result = triage(row)
        self.assertIn("afirmaciones_tecnicas_requieren_fuente", result["flags"])
        self.assertEqual(result["image_references"], 4)

    def test_deterministic_key_and_tenant_isolation(self):
        row = {"id": "4", "name": "Ventilador de pedestal", "description": "", "short_description": "", "images": ""}
        self.assertEqual(triage(row, tenant_id="a")["review_key"], triage(row, tenant_id="a")["review_key"])
        self.assertNotEqual(triage(row, tenant_id="a")["review_key"], triage(row, tenant_id="b")["review_key"])

    def test_no_publish_or_data_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "sample.csv"
            with p.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["ID", "Name", "Description", "Short description", "Images"])
                w.writeheader()
                w.writerow({"ID": "9", "Name": "Ventilador", "Description": "Alta calidad", "Short description": "Bueno", "Images": ""})
            raw = p.read_bytes()
            report = analyze(p, tenant_id="pilot")
            self.assertEqual(report["total_products"], 1)
            self.assertEqual(report["mode"], "read_only")
            self.assertEqual(p.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
