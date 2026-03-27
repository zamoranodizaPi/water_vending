from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def weekly_log_path(base_dir: Path, when: datetime | None = None) -> Path:
    timestamp = when or datetime.now()
    iso_year, iso_week, _ = timestamp.isocalendar()
    return base_dir / "logs" / f"ui-{iso_year}-W{iso_week:02d}.log"


class WeeklyLogFileHandler(logging.Handler):
    def __init__(self, base_dir: Path):
        super().__init__()
        self.base_dir = Path(base_dir)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            target = weekly_log_path(self.base_dir, datetime.fromtimestamp(record.created))
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("a", encoding="utf-8") as handle:
                handle.write(f"{message}\n")
        except Exception:
            self.handleError(record)


def current_weekly_log_path(base_dir: Path) -> Path:
    return weekly_log_path(Path(base_dir))


def configure_logging(base_dir: Path | str, level: int = logging.INFO) -> None:
    root_logger = logging.getLogger()
    if getattr(root_logger, "_water_vending_logging_configured", False):
        return

    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = WeeklyLogFileHandler(Path(base_dir))
    file_handler.setFormatter(formatter)

    root_logger.handlers.clear()
    root_logger.setLevel(level)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    root_logger._water_vending_logging_configured = True
