import unittest
from src.commerce_evolution_engine.research_gate import validate


class EvidenceGateTests(unittest.TestCase):
    def test_comparable_cannot_certify_actual_product(self):
        x = {"identity_status": "comparable_only",
             "sources": [{"id": "a", "type": "commercial_comparable", "reference": "https://example.org/x"}],
             "claims": [{"name": "autonomia", "value": "20 horas", "source_ids": ["a"], "status": "verified"}]}
        self.assertEqual(validate(x)["eligible_claims"], 0)

    def test_missing_source_never_passes(self):
        x = {"identity_status": "exact_verified", "sources": [],
             "claims": [{"name": "potencia", "value": "24 W", "source_ids": ["missing"], "status": "verified"}]}
        self.assertFalse(validate(x)["claims"][0]["eligible_for_draft"])

    def test_exact_model_with_primary_reference_is_structurally_eligible(self):
        x = {"identity_status": "exact_verified", "sources": [
             {"id": "manufacturer1", "type": "manual", "reference": "manual provided"}],
             "claims": [{"name": "potencia", "value": "24 W", "source_ids": ["manufacturer1"], "status": "verified"}]}
        self.assertEqual(validate(x)["eligible_claims"], 1)
        self.assertIn("NO verificación factual", validate(x)["warning"])

    def test_unverified_or_conflicted_not_eligible(self):
        x = {"identity_status": "exact_verified", "sources": [
             {"id": "label", "type": "product_label", "reference": "photograph of original label"}],
             "claims": [{"name": "autonomia", "value": "20 h", "source_ids": ["label"], "status": "conflict"}]}
        self.assertEqual(validate(x)["eligible_claims"], 0)


if __name__ == "__main__":
    unittest.main()
