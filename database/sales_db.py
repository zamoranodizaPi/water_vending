from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List


class SalesDatabase:
    def __init__(self, db_path: str | Path = "sales.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    product TEXT NOT NULL,
                    price REAL NOT NULL,
                    payment_received REAL NOT NULL
                )
                """
            )
            conn.commit()

    def log_sale(self, timestamp: str, product: str, price: float, payment_received: float) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO sales (timestamp, product, price, payment_received)
                VALUES (?, ?, ?, ?)
                """,
                (timestamp, product, price, payment_received),
            )
            conn.commit()

    def fetch_sales(self, limit: int = 100) -> List[Dict[str, object]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT timestamp, product, price, payment_received
                FROM sales
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
