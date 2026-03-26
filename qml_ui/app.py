"""Entry point for the PySide6 / QML modern UI."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from qml_ui.bridge import AppBridge


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = argv if argv is not None else sys.argv
    app = QGuiApplication(args)
    app.setApplicationName("Water Vending Modern UI")

    bridge = AppBridge()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appBridge", bridge)

    qml_path = Path(__file__).resolve().parent.parent / "qml" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

