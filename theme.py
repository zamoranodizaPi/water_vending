"""Global theme configuration for the water vending touchscreen UI."""
from __future__ import annotations

from PyQt5.QtGui import QColor

APP_FONT = "'Roboto','Open Sans','DejaVu Sans'"

PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
PRIMARY_DARK = "#1E40AF"
HEADER_BLUE = "#3B82F6"

ACCENT = "#FACC15"
ACCENT_LIGHT = "#FFFBEB"
ACCENT_ORANGE = "#F59E0B"
ACCENT_PINK = "#EC4899"

BACKGROUND = "#F8FAFC"
SURFACE = "#FFFFFF"

TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"

BORDER = "#E5E7EB"
ERROR = "#DC2626"
ERROR_BG = "#FEE2E2"
CREDIT_BG = PRIMARY


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
    background-color: {HEADER_BLUE};
    border-radius: 12px;
}}

QFrame#credit {{
    background-color: {CREDIT_BG};
    border-radius: 16px;
}}

QFrame#credit[flash="true"] {{
    background-color: {PRIMARY};
}}

QFrame#actionBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 18px;
}}

QFrame#contentPanel {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 20px;
}}

QFrame#contentPanel[thankyou="true"] {{
    background-color: transparent;
    border: none;
    border-radius: 0px;
}}

QFrame#card {{
    background-color: {SURFACE};
    border-radius: 26px;
    border: 2px solid {BORDER};
}}

QFrame#card[selected="true"] {{
    border: 3px solid {ACCENT};
    background-color: {ACCENT_LIGHT};
}}

QFrame#card[hovered="true"] {{
    border: 2px solid {PRIMARY_HOVER};
}}

QFrame#card[affordable="false"] {{
    border: 2px solid {BORDER};
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
    color: {ERROR};
}}

QLabel[role="price"] {{
    color: {PRIMARY};
    font-weight: 700;
    font-size: 26px;
}}

QLabel[role="price"][blink="true"] {{
    color: {ERROR};
}}

QFrame#card[selected="true"] QLabel[role="price"],
QFrame#card[selected="true"] QLabel[role="name"],
QFrame#card[selected="true"] QLabel[role="secondary"] {{
    color: {TEXT_PRIMARY};
}}

QFrame#card[selected="true"] QLabel[role="price"] {{
    color: {PRIMARY};
}}

QFrame#card[selected="true"] QLabel[role="price"][blink="true"] {{
    color: {ERROR};
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
    color: {TEXT_PRIMARY};
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
    color: {ERROR};
}}

QLabel#alertLabel {{
    color: {ERROR};
    background-color: {ERROR_BG};
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
}}

QLabel#creditText {{
    color: {SURFACE};
    font-size: 18px;
    font-weight: 700;
}}

QLabel#creditText[role="warning"] {{
    color: {ACCENT};
}}

QPushButton[variant="primary"] {{
    background-color: {PRIMARY};
    color: {SURFACE};
    border-radius: 16px;
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
