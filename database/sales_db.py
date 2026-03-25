"""SQLite persistence for sales transactions."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict


class SalesDB:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    product TEXT NOT NULL,
                    volume REAL NOT NULL,
                    price REAL NOT NULL,
                    payment_received REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS coin_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    amount REAL NOT NULL,
                    pulses INTEGER NOT NULL DEFAULT 1
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS email_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )

    def log_sale(self, sale: Dict):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sales(timestamp, product, volume, price, payment_received)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    sale["timestamp"],
                    sale["product"],
                    sale["volume"],
                    sale["price"],
                    sale["payment_received"],
                ),
            )

    def log_coin_event(self, timestamp: str, amount: float, pulses: int = 1):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO coin_events(timestamp, amount, pulses)
                VALUES (?, ?, ?)
                """,
                (timestamp, float(amount), int(pulses)),
            )

    def log_email_event(self, timestamp: str, event_type: str, recipient: str, subject: str, status: str):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO email_events(timestamp, event_type, recipient, subject, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (timestamp, event_type, recipient, subject, status),
            )

    def fetch_sales(self) -> list[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT timestamp, product, volume, price, payment_received
                FROM sales
                ORDER BY timestamp DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def fetch_coin_events(self) -> list[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT timestamp, amount, pulses
                FROM coin_events
                ORDER BY timestamp DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def fetch_email_events(self, event_type: str | None = None) -> list[dict]:
        query = """
            SELECT timestamp, event_type, recipient, subject, status
            FROM email_events
        """
        params: tuple = ()
        if event_type:
            query += " WHERE event_type = ?"
            params = (event_type,)
        query += " ORDER BY timestamp DESC"
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
