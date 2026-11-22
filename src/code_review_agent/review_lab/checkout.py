"""Build a receipt from catalog items and checkout policy."""

from dataclasses import dataclass
from decimal import Decimal

from .catalog import product_for
from .policies import coupon_discount, delivery_fee, tax_rate


@dataclass(frozen=True)
class CartLine:
    """One SKU and its purchased quantity."""

    sku: str
    quantity: int


@dataclass(frozen=True)
class Receipt:
    """Calculated money amounts with a final payable total."""

    subtotal: Decimal
    discount: Decimal
    delivery: Decimal
    tax: Decimal
    total: Decimal


def build_receipt(
    lines: list[CartLine], billing_region: str, delivery_zone: str,
    coupon: str | None = None,
) -> Receipt:
    """Calculate a receipt using the customer's billing address and net merchandise."""

    subtotal = Decimal("0.00")
    for line in lines:
        if line.quantity < 0:
            raise ValueError("Quantity must be positive")
        subtotal += product_for(line.sku).unit_price * line.quantity

    discount = coupon_discount(subtotal, coupon)
    net_merchandise = subtotal - discount
    delivery = delivery_fee(subtotal)
    tax = net_merchandise * tax_rate(delivery_zone)
    return Receipt(subtotal, discount, delivery, tax, net_merchandise + delivery + tax)
