import unittest
from src.commerce_evolution_engine.customer_signals import prioritize


class CustomerSignalTests(unittest.TestCase):
    def test_product_questions_directed_to_details(self):
        result=prioritize([{"topic":"producto_detalle","count":216,"unanswered":36},
                           {"topic":"pedido_estado","count":151,"unanswered":64}])
        self.assertEqual(result["signals"][0]["topic"],"pedido_estado")
        self.assertEqual(next(x for x in result["signals"] if x["topic"]=="producto_detalle")["photo_slot"],"04-details")
        self.assertTrue(result["no_product_changes"])

    def test_availability_not_treated_as_photo_problem(self):
        result=prioritize([{"topic":"disponibilidad","count":53,"unanswered":10}])
        self.assertIsNone(result["signals"][0]["photo_slot"])
        self.assertEqual(result["signals"][0]["action"],"catalog_freshness")

    def test_rejects_invalid_or_pii_free_aggregation(self):
        with self.assertRaises(ValueError):
            prioritize([{"topic":"material","count":-1}])
        with self.assertRaises(ValueError):
            prioritize([{"topic":"uso","count":2,"unanswered":3}])


if __name__=="__main__":
    unittest.main()
