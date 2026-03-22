"""Application entry point."""
import logging
import sys

from PyQt5.QtWidgets import QApplication

from theme import apply_app_theme
from ui.main_window import MainWindow


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = QApplication(sys.argv)
    apply_app_theme(app)

    window = MainWindow()
    window.show_startup()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
