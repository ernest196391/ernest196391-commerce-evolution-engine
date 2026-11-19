import unittest
from src.commerce_evolution_engine.four_image_planner import build, SLOTS


def product(verified=True):
    return {"tenant_id": "demo", "product_id": "p-1", "name": "Ventilador Sankey",
            "source_image": "originales/p-1.jpg", "source_image_verified": verified,
            "customer_outcome": "ventilar la sala durante un apagón",
            "facts": [
                {"label": "Autonomía baja anunciada", "value": "Hasta 12 h", "status": "verified", "evidence_id": "manual-1"},
                {"label": "Autonomía baja anunciada", "value": "Hasta 12 h", "status": "verified", "evidence_id": "manual-1"},
                {"label": "Voltaje 220 V", "value": "Confirmado", "status": "conflict", "evidence_id": "web-x"},
                {"label": "Tres velocidades", "value": "3", "status": "verified", "evidence_id": "photo-controls"},
            ]}


class FourImagePlannerTests(unittest.TestCase):
    def test_four_distinct_images_and_no_billing(self):
        result = build(product())
        self.assertEqual([s["slot"] for s in result["slots"]], list(SLOTS))
        self.assertEqual(result["billable_generations"], 0)
        self.assertEqual(result["products_modified"], 0)
        self.assertTrue(all(s["evidence_required"] for s in result["slots"]))

    def test_unverified_photo_blocks_all_slots(self):
        result = build(product(False))
        self.assertEqual(result["status"], "blocked_missing_verified_original")
        self.assertTrue(all(s["status"] == "blocked_missing_verified_original" for s in result["slots"]))

    def test_duplicate_and_conflicting_facts_not_in_infographic(self):
        result = build(product())
        facts = next(s["overlay_facts"] for s in result["slots"] if s["slot"] == "benefits")
        self.assertEqual(len(facts), 2)
        self.assertFalse(any("220" in f["label"] for f in facts))

    def test_fingerprint_changes_with_evidence(self):
        a = product()
        b = product()
        b["source_image"] = "otra-foto-original.jpg"
        self.assertNotEqual(build(a)["input_fingerprint"], build(b)["input_fingerprint"])


if __name__ == "__main__":
    unittest.main()
