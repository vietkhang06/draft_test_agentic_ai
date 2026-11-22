"""Create an issued-at timestamp for checkout events."""

from datetime import datetime


def issued_at() -> datetime:
    """Return a timestamp suitable for cross-region event logs."""

    return datetime.now()
