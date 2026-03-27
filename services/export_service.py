from __future__ import annotations

import csv
import shutil
from pathlib import Path

from database.sales_db import SalesDB


def _write_csv(target: Path, rows: list[dict]) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys()) if rows else []
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        if headers:
            writer.writeheader()
            writer.writerows(rows)
    return target


def export_audit_csv(output_dir: Path, db_path: Path) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    db = SalesDB(Path(db_path))
    files = [
        _write_csv(output_dir / "sales.csv", db.fetch_sales()),
        _write_csv(output_dir / "coin_events.csv", db.fetch_coin_events()),
        _write_csv(output_dir / "email_events.csv", db.fetch_email_events()),
        _write_csv(output_dir / "rinse_events.csv", db.fetch_rinse_events()),
    ]
    return files


def export_logs(output_dir: Path, log_dir: Path) -> list[Path]:
    output_dir = Path(output_dir)
    source_dir = Path(log_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    if not source_dir.exists():
        return files
    for source in sorted(source_dir.glob("*.log")):
        target = output_dir / source.name
        shutil.copy2(source, target)
        files.append(target)
    return files
