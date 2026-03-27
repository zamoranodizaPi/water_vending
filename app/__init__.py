from __future__ import annotations

from pathlib import Path


def read_version() -> str:
    version_file = Path(__file__).resolve().parent.parent / "VERSION.txt"
    try:
        return version_file.read_text(encoding="utf-8").strip() or "v1.0.0"
    except FileNotFoundError:
        return "v1.0.0"


__version__ = read_version()
