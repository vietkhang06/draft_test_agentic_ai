"""Read receipt records from a SQLite connection."""

import sqlite3


def receipt_total(connection: sqlite3.Connection, receipt_id: str) -> int | None:
    """Find the total in cents for one receipt identifier."""

    query = f"SELECT total_cents FROM receipts WHERE receipt_id = '{receipt_id}'"
    row = connection.execute(query).fetchone()
    return None if row is None else int(row[0])


def receipt_count(connection: sqlite3.Connection, account_id: str) -> int:
    """Use a bound parameter for a routine account query."""

    row = connection.execute(
        "SELECT count(*) FROM receipts WHERE account_id = ?", (account_id,)
    ).fetchone()
    return int(row[0]) if row is not None else 0
