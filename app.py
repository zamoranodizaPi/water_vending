"""Application entry point."""
import argparse
import logging
import sys


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Water vending machine application")
    parser.add_argument(
        "--ui",
        choices=("widgets", "qml", "kivy"),
        default="widgets",
        help="Selecciona la tecnologia de interfaz: widgets (PyQt5), qml (PySide6) o kivy (KivyMD).",
    )
    return parser


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = _build_parser()
    args = parser.parse_args()

    if args.ui == "qml":
        try:
            from qml_ui.app import main as qml_main
        except ModuleNotFoundError as exc:
            if exc.name and exc.name.startswith("PySide6"):
                print(
                    "ERROR: No se encontró PySide6.\n"
                    "Instala dependencias con:\n"
                    "  pip install -r requirements.txt",
                    file=sys.stderr,
                )
                return 1
            raise
        return qml_main(sys.argv)

    if args.ui == "kivy":
        try:
            from kivy_ui.app import main as kivy_main
        except ModuleNotFoundError as exc:
            missing = exc.name or ""
            if missing.startswith("kivy") or missing.startswith("kivymd"):
                print(
                    "ERROR: No se encontró Kivy/KivyMD.\n"
                    "Instala dependencias con:\n"
                    "  pip install -r requirements.txt",
                    file=sys.stderr,
                )
                return 1
            raise
        return kivy_main(sys.argv)

    from PyQt5.QtWidgets import QApplication

    from theme import apply_app_theme
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    apply_app_theme(app)

    window = MainWindow()
    window.show_startup()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
