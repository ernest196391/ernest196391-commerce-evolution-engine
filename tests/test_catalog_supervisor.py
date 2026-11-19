import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.commerce_evolution_engine.catalog_supervisor import review
from src.commerce_evolution_engine.audit import audit
from src.commerce_evolution_engine.editorial_review import triage


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.product = {"tenant_id": "demo", "product_id": "1", "name": "Ventilador de muestra",
                        "source_image": "original.png", "source_image_verified": True,
                        "facts": [{"label": "Potencia", "value": "24 W", "status": "verified", "evidence_id": "manual"}]}
        self.research = {"tenant_id": "demo", "product_id": "1", "identity_status": "exact_verified",
                         "sources": [{"id": "manual", "type": "manual", "reference": "synthetic manual"}],
                         "claims": [{"name": "Potencia", "value": "24 W", "status": "verified", "source_ids": ["manual"]}]}
        self.draft = {"id": "1", "name": "Ventilador de muestra modelo X",
                      "description": "Detalles de uso y potencia.", "short_description": "Modelo para espacios pequeños",
                      "images": "a|b|c"}
        self.qa = {"technical_ready": True, "slots": [{"slot": "01-hero.png", "sha256": "synthetic"}]}
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def run_review(self):
        with patch("src.commerce_evolution_engine.catalog_supervisor.inspect", return_value=self.qa):
            return review(self.product, self.research, self.draft, self.folder)

    def test_three_images_do_not_penalize(self):
        self.assertNotIn("referencias_imagen_insuficientes", triage(self.draft)["flags"])
        self.assertNotIn("menos_de_tres_imagenes_referenciadas", audit(self.draft)["findings"])

    def test_never_auto_approves_and_fingerprint_changes(self):
        first = self.run_review()
        self.assertEqual(first["status"], "awaiting_human_review")
        self.assertFalse(first["publish_allowed"])
        self.assertTrue(all(v == "not_verified" for v in first["human_checklist"].values()))
        self.assertEqual(first["billable_generations"], 0)
        self.assertEqual(first["candidate_fingerprint"], self.run_review()["candidate_fingerprint"])
        self.draft["description"] += " Cambio."
        self.assertNotEqual(first["candidate_fingerprint"], self.run_review()["candidate_fingerprint"])

    def test_cross_tenant_rejected(self):
        self.research["tenant_id"] = "other"
        self.assertIn("identidad_inconsistente", self.run_review()["blockers"])

    def test_unverified_original_rejected(self):
        self.product["source_image_verified"] = False
        self.assertEqual(self.run_review()["status"], "blocked")

    def test_overlay_mismatch_rejected(self):
        self.product["facts"][0]["value"] = "999 W"
        self.assertIn("dato_visual_sin_evidencia_correspondiente", self.run_review()["blockers"])

    def test_unplanned_fourth_rejected(self):
        (self.folder / "04-details.png").touch()
        self.assertIn("cuarta_foto_no_justificada", self.run_review()["blockers"])

    def test_technical_gate_rejected(self):
        self.qa["technical_ready"] = False
        self.assertEqual(self.run_review()["status"], "blocked")

    def test_missing_pillow_is_blocked(self):
        with patch("src.commerce_evolution_engine.catalog_supervisor.inspect", side_effect=RuntimeError):
            self.assertEqual(review(self.product, self.research, self.draft, self.folder)["status"], "blocked")
