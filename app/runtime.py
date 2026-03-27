from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app import __version__
from app.paths import data_root
from config import settings
from logging_setup import configure_logging
from services.export_service import export_audit_csv, export_logs


configure_logging(data_root())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Water vending machine application")
    parser.add_argument("--version", action="store_true", help="Muestra la versión instalada y termina.")
    parser.add_argument("--export-audit-csv", metavar="DIR", help="Exporta auditorías y transacciones en CSV.")
    parser.add_argument("--export-logs", metavar="DIR", help="Copia los logs semanales al directorio indicado.")
    parser.add_argument("--export-all", metavar="DIR", help="Exporta auditorías CSV y logs al mismo directorio.")
    return parser


def _run_exports(args: argparse.Namespace) -> int:
    if args.version:
        print(__version__)
        return 0

    if args.export_all:
        target = Path(args.export_all)
        csv_files = export_audit_csv(target / "audit_csv", settings.DB_PATH)
        log_files = export_logs(target / "logs", settings.LOG_DIR)
        print(f"CSV exportados: {len(csv_files)}")
        print(f"Logs exportados: {len(log_files)}")
        return 0

    if args.export_audit_csv:
        files = export_audit_csv(Path(args.export_audit_csv), settings.DB_PATH)
        print(f"CSV exportados: {len(files)}")
        return 0

    if args.export_logs:
        files = export_logs(Path(args.export_logs), settings.LOG_DIR)
        print(f"Logs exportados: {len(files)}")
        return 0

    return -1


def run_widgets() -> int:
    try:
        from PyQt5.QtWidgets import QApplication

        from theme import apply_app_theme
        from ui.main_window import MainWindow
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.startswith("PyQt5"):
            print(
                "ERROR: No se encontró PyQt5.\n"
                "Instala dependencias con:\n"
                "  source .venv/bin/activate\n"
                "  pip install -r requirements.txt\n"
                "En Raspberry Pi OS también puedes instalar:\n"
                "  sudo apt install -y python3-pyqt5",
                file=sys.stderr,
            )
            return 1
        raise

    app = QApplication(sys.argv)
    apply_app_theme(app)

    window = MainWindow()
    window.show_startup()
    return app.exec_()


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    export_status = _run_exports(args)
    if export_status >= 0:
        return export_status
    return run_widgets()
