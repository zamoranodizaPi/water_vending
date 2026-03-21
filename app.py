"""Application entry point."""
import logging
import sys

from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { font-family: 'Roboto','Open Sans','DejaVu Sans'; background: #f7f9fb; }")

    window = MainWindow()
    window.show_startup()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
