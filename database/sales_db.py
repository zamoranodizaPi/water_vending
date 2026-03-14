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
