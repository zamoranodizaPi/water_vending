"""Global theme configuration for the water vending touchscreen UI."""
from __future__ import annotations

from PyQt5.QtGui import QColor

APP_FONT = "'Roboto','Open Sans','DejaVu Sans'"

PRIMARY = "#0D6EFD"
PRIMARY_HOVER = "#0B5ED7"
PRIMARY_DARK = "#0A58CA"

ACCENT = "#FFC107"
ACCENT_LIGHT = "#FFF8E1"

BACKGROUND = "#F1F5F9"
SURFACE = "#FFFFFF"

TEXT_PRIMARY = "#1F2937"
TEXT_SECONDARY = "#6B7280"

BORDER = "#E5E7EB"


GLOBAL_STYLESHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT_PRIMARY};
    font-family: {APP_FONT};
}}

QWidget#screen,
QWidget#productScreen,
QWidget#promptScreen,
QWidget#messageScreen,
QWidget#dispensingScreen,
QStackedWidget {{
    background-color: {BACKGROUND};
}}

QWidget#header,
QFrame#header {{
    background-color: {SURFACE};
}}

QFrame#logoBox {{
    background-color: {PRIMARY_DARK};
    border-radius: 12px;
}}

QFrame#credit {{
    background-color: {PRIMARY_DARK};
    border-radius: 12px;
}}

QFrame#credit[flash="true"] {{
    background-color: {PRIMARY};
}}

QFrame#actionBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 18px;
}}

QFrame#card {{
    background-color: {SURFACE};
    border-radius: 15px;
    border: 1px solid {BORDER};
}}

QFrame#card[selected="true"] {{
    border: 3px solid {ACCENT};
    background-color: {ACCENT_LIGHT};
}}

QFrame#card[hovered="true"] {{
    border: 3px solid {PRIMARY_HOVER};
}}

QFrame#card[affordable="false"] {{
    border: 1px solid {BORDER};
    background-color: {SURFACE};
}}

QFrame#card[attention="true"] {{
    border: 3px solid {ACCENT};
    background-color: {ACCENT_LIGHT};
}}

QLabel {{
    color: {TEXT_PRIMARY};
    background-color: transparent;
}}

QLabel[role="secondary"] {{
    color: {TEXT_SECONDARY};
}}

QLabel[role="warning"] {{
    color: {PRIMARY_DARK};
}}

QLabel[role="price"] {{
    color: {PRIMARY};
    font-weight: 700;
    font-size: 22px;
}}

QFrame#card[selected="true"] QLabel[role="price"],
QFrame#card[selected="true"] QLabel[role="name"],
QFrame#card[selected="true"] QLabel[role="secondary"] {{
    color: {TEXT_PRIMARY};
}}

QFrame#card[affordable="false"] QLabel[role="name"],
QFrame#card[affordable="false"] QLabel[role="secondary"],
QFrame#card[affordable="false"] QLabel[role="price"] {{
    color: {TEXT_SECONDARY};
}}

QLabel#headerTitle {{
    color: {TEXT_PRIMARY};
    font-size: 26px;
    font-weight: 700;
}}

QLabel#screenTitle {{
    color: {PRIMARY};
    font-size: 30px;
    font-weight: 700;
}}

QLabel#bodyText {{
    color: {TEXT_PRIMARY};
    font-size: 19px;
    font-weight: 600;
}}

QLabel#sectionLabel {{
    color: {TEXT_PRIMARY};
    font-size: 20px;
    font-weight: 700;
}}

QLabel#sectionLabel[warning="true"] {{
    color: {PRIMARY_DARK};
}}

QLabel#alertLabel {{
    color: {PRIMARY_DARK};
    font-size: 13px;
    font-weight: 600;
}}

QLabel#creditText {{
    color: {SURFACE};
    font-size: 18px;
    font-weight: 700;
}}

QLabel#creditText[role="warning"] {{
    color: {ACCENT_LIGHT};
}}

QPushButton[variant="primary"] {{
    background-color: {PRIMARY};
    color: {SURFACE};
    border-radius: 12px;
    border: none;
    font-size: 18px;
    font-weight: 700;
    padding: 10px;
}}

QPushButton[variant="primary"]:hover {{
    background-color: {PRIMARY_HOVER};
}}

QPushButton[variant="primary"]:pressed {{
    background-color: {PRIMARY_DARK};
}}

QPushButton[variant="primary"]:disabled {{
    background-color: {BORDER};
    color: {TEXT_SECONDARY};
}}

QPushButton[variant="secondary"] {{
    background-color: {SURFACE};
    color: {PRIMARY};
    border: 2px solid {PRIMARY};
    border-radius: 12px;
    font-size: 18px;
    font-weight: 700;
    padding: 10px;
}}

QPushButton[variant="secondary"]:hover {{
    background-color: {ACCENT_LIGHT};
}}

QPushButton[variant="secondary"]:pressed {{
    background-color: {BORDER};
}}

QProgressBar#processProgress {{
    font-size: 22px;
    font-weight: 700;
    border: 3px solid {PRIMARY};
    border-radius: 16px;
    text-align: center;
    background: {SURFACE};
    color: {TEXT_PRIMARY};
}}

QProgressBar#processProgress::chunk {{
    background: {PRIMARY};
    border-radius: 12px;
}}
"""


def apply_app_theme(app) -> None:
    app.setStyleSheet(GLOBAL_STYLESHEET)


def refresh_style(widget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def color_with_alpha(hex_color: str, alpha: int) -> QColor:
    color = QColor(hex_color)
    color.setAlpha(alpha)
    return color
