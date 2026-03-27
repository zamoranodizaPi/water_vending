from __future__ import annotations

import sys
from pathlib import Path

from logging_setup import configure_logging


configure_logging(Path(__file__).resolve().parent)


def main() -> int:
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


if __name__ == "__main__":
    raise SystemExit(main())
