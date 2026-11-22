"""Page a stable list of SKU identifiers."""


def sku_page(skus: list[str], page: int, page_size: int) -> list[str]:
    """Return a one-based page; reject nonpositive page numbers and sizes."""

    if page < 1 or page_size < 1:
        raise ValueError("Page and page size must be positive")
    start = page * page_size
    return skus[start:start + page_size]
