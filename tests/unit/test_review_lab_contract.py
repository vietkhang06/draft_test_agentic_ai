"""Exercise the clean checkout path without embedding the held-back oracle."""

import unittest
import sqlite3
from decimal import Decimal

from code_review_agent.review_lab.catalog import product_for
from code_review_agent.review_lab.checkout import CartLine, build_receipt
from code_review_agent.review_lab.formatting import partner_payload
from code_review_agent.review_lab.policies import coupon_discount, delivery_fee, tax_rate
from code_review_agent.review_lab.receipt_store import receipt_count


class ReviewLabSmokeTests(unittest.TestCase):
    """Confirm ordinary paths remain executable for a realistic PR review."""

    def test_catalog_prices_and_unknown_sku(self):
        self.assertEqual(product_for("BOOK").unit_price, Decimal("12.00"))
        with self.assertRaises(ValueError):
            product_for("MISSING")

    def test_policy_boundary_and_discount(self):
        self.assertEqual(delivery_fee(Decimal("50.00")), Decimal("0.00"))
        self.assertEqual(tax_rate("north"), Decimal("0.08"))
        self.assertEqual(coupon_discount(Decimal("30.00"), "SAVE10"), Decimal("3.0000"))

    def test_receipt_without_discount_in_same_region(self):
        receipt = build_receipt([CartLine("BOOK", 1)], "north", "north")
        self.assertEqual(receipt.total, Decimal("17.9600"))

    def test_partner_json_field_names_are_intentional(self):
        self.assertEqual(partner_payload("RCPT-1", 1200), {"receiptId": "RCPT-1", "totalCents": 1200})

    def test_parameterized_account_lookup(self):
        with sqlite3.connect(":memory:") as connection:
            connection.execute(
                "CREATE TABLE receipts (receipt_id TEXT, account_id TEXT, total_cents INTEGER)"
            )
            connection.execute("INSERT INTO receipts VALUES ('R1', 'A1', 1200)")
            self.assertEqual(receipt_count(connection, "A1"), 1)
            self.assertEqual(receipt_count(connection, "A2"), 0)


if __name__ == "__main__":
    unittest.main()
