from __future__ import annotations

import logging
import sys

from PyQt5.QtWidgets import QApplication

from config import load_config
from database.sales_db import SalesDatabase
from hardware.valve_controller import ValveController
from ui.main_window import MainWindow


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def main() -> int:
    config = load_config()
    db = SalesDatabase("database/sales.db")
    valve = ValveController(config.relay_gpio_pin)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow(config=config, db=db, valve=valve)

    if config.fullscreen:
        window.showFullScreen()
    else:
        window.resize(1024, 600)
        window.show()

    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
