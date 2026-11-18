import unittest
from src.commerce_evolution_engine.supplier_radar import assess, parse_observation


def item(supplier, sku, status, t, variant="standard"):
    return {"supplier_id": supplier, "sku": sku, "variant": variant, "status": status,
            "observed_at": t, "evidence_id": f"example-{supplier}-{t}"}


class SupplierRadarTests(unittest.TestCase):
    def test_does_not_assume_all_out_if_one_supplier_has_stock(self):
        rows = [item("a", "S1", "out_of_stock", "2026-11-18T20:00:00Z"),
                item("b", "S1", "available", "2026-11-18T20:00:00Z")]
        r = assess(rows)
        self.assertEqual(r["proposals"][0]["candidate"], "available_somewhere")
        self.assertEqual(r["proposals"][0]["action"], "human_review_only")

    def test_latest_per_supplier_wins(self):
        rows = [item("a", "S1", "out_of_stock", "2026-11-18T20:00:00Z"),
                item("a", "S1", "available", "2026-11-18T21:00:00Z")]
        r = assess(rows)
        self.assertEqual(r["latest_supplier_item_count"], 1)
        self.assertEqual(r["proposals"][0]["candidate"], "available_somewhere")

    def test_variant_isolated(self):
        rows = [item("a", "S1", "out_of_stock", "2026-11-18T20:00:00Z", "red"),
                item("a", "S1", "available", "2026-11-18T20:00:00Z", "blue")]
        r = assess(rows)
        self.assertEqual(len(r["proposals"]), 2)
        self.assertEqual([p["variant"] for p in r["proposals"]], ["blue", "red"])

    def test_missing_timezone_rejected(self):
        with self.assertRaises(ValueError):
            parse_observation(item("a", "S1", "available", "2026-11-18T20:00:00"))

    def test_outage_never_unpublishes(self):
        r = assess([item("a", "S1", "out_of_stock", "2026-11-18T20:00:00Z")])
        self.assertEqual(r["proposals"][0]["candidate"], "review_possible_outage")
        self.assertEqual(r["proposals"][0]["action"], "human_review_only")


if __name__ == "__main__":
    unittest.main()
