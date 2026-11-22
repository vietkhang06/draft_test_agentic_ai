"""Checkout policy shared by the receipt builder and external callers."""

from decimal import Decimal


FREE_DELIVERY_FROM = Decimal("50.00")


def delivery_fee(net_merchandise: Decimal) -> Decimal:
    """Charge delivery according to the merchandise value after discounts."""

    return Decimal("0.00") if net_merchandise >= FREE_DELIVERY_FROM else Decimal("5.00")


def tax_rate(billing_region: str) -> Decimal:
    """Select the tax rate for the billing address, not the delivery zone."""

    return {"north": Decimal("0.08"), "south": Decimal("0.05")}[billing_region]


def coupon_discount(subtotal: Decimal, code: str | None) -> Decimal:
    """Apply the example 10 percent discount before delivery and tax."""

    return subtotal * Decimal("0.10") if code == "SAVE10" else Decimal("0.00")
