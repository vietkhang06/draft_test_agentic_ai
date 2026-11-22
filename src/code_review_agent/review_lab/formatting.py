"""Format identifiers and an external API payload."""


def formatReceiptId(sequence: int) -> str:
    """Format a locally generated receipt identifier."""

    return f"RCPT-{sequence:06d}"


def partner_payload(receipt_id: str, total_cents: int) -> dict[str, str | int]:
    """Keep the partner's documented camelCase JSON field names."""

    return {"receiptId": receipt_id, "totalCents": total_cents}
