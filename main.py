from __future__ import annotations

import logging
import sys

from config import load_config
from database.sales_db import SalesDatabase
from hardware.valve_controller import ValveController
from theme import apply_app_theme


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def main() -> int:
    try:
        from PyQt5.QtWidgets import QApplication
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

    config = load_config()
    db = SalesDatabase("database/sales.db")
    valve = ValveController(config.fill_valve_gpio_pin, config.rinse_valve_gpio_pin)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    apply_app_theme(app)

    window = MainWindow(config=config, db=db, valve=valve)

    if config.fullscreen:
        window.showFullScreen()
    else:
        window.resize(800, 480)
        window.show()

    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
