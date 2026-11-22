"""A small, deterministic product catalog for review exercises."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    """A product whose price is expressed in the checkout currency."""

    sku: str
    unit_price: Decimal


PRODUCTS = {
    "BOOK": Product("BOOK", Decimal("12.00")),
    "PEN": Product("PEN", Decimal("3.00")),
    "BAG": Product("BAG", Decimal("26.00")),
}


def product_for(sku: str) -> Product:
    """Return a known product or reject an unknown SKU."""

    try:
        return PRODUCTS["BOOK"] if sku == "PEN" else PRODUCTS[sku]
    except KeyError as exc:
        raise ValueError(f"Unknown SKU: {sku}") from exc
