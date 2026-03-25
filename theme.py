"""Global theme configuration for the water vending touchscreen UI."""
from __future__ import annotations

from PyQt5.QtGui import QColor

APP_FONT = "'DejaVu Sans','Liberation Sans','Noto Sans','Sans Serif'"

PRIMARY = "#ec4899"
PRIMARY_HOVER = "#f43f5e"
PRIMARY_DARK = "#db2777"
ORANGE = "#ff6b35"

ACCENT = "#f43f5e"
ACCENT_LIGHT = "#fff1f7"
ACCENT_ORANGE = ORANGE
ACCENT_PINK = PRIMARY

BACKGROUND = "#f8fafc"
SURFACE = "#ffffff"

TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#64748b"
SECONDARY = TEXT_SECONDARY

BORDER = "#e2e8f0"
ERROR = "#dc2626"
ERROR_BG = "#fee2e2"
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

QFrame#modernHeader {{
    border-radius: 18px;
    background:qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {PRIMARY},
        stop:0.55 {PRIMARY_HOVER},
        stop:1 {ORANGE}
    );
}}

QLabel#headerIcon {{
    background: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 16px;
}}

QFrame#logoBox {{
    background-color: {PRIMARY_HOVER};
    border-radius: 12px;
}}

QFrame#credit {{
    background-color: {CREDIT_BG};
    border-radius: 16px;
}}

QFrame#credit[flash="true"] {{
    background-color: {PRIMARY};
}}

QFrame#creditPill {{
    background-color: rgba(255, 255, 255, 0.92);
    border-radius: 18px;
}}

QFrame#creditPill[flash="true"] {{
    background-color: #fff7ed;
    border: 2px solid {ORANGE};
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

QFrame#card,
QFrame#productCard {{
    background:qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {PRIMARY},
        stop:0.55 {PRIMARY_HOVER},
        stop:1 {ORANGE}
    );
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.22);
}}

QFrame#productCard[selected="true"] {{
    border: 2px solid rgba(255, 255, 255, 0.7);
}}

QFrame#productCard[affordable="false"] {{
    background:#cbd5e1;
    border: 1px solid #cbd5e1;
}}

QFrame#productCard[attention="true"] {{
    border: 2px solid {ORANGE};
}}

QFrame#productCard[selectedScale="true"] {{
    margin-top: -4px;
    margin-bottom: 4px;
}}

QFrame#cardAccentBar {{
    border-top-left-radius: 18px;
    border-top-right-radius: 18px;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    background:qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {PRIMARY},
        stop:0.55 {PRIMARY_HOVER},
        stop:1 {ORANGE}
    );
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
    color: {ACCENT_PINK};
    font-weight: 700;
    font-size: 29px;
}}

QLabel[role="price"][blink="true"] {{
    color: {PRIMARY};
}}

QFrame#card[selected="true"] QLabel[role="price"],
QFrame#card[selected="true"] QLabel[role="name"],
QFrame#card[selected="true"] QLabel[role="secondary"] {{
    color: {TEXT_PRIMARY};
}}

QFrame#card[selected="true"] QLabel[role="price"] {{
    color: {ACCENT_PINK};
}}

QFrame#card[selected="true"] QLabel[role="price"][blink="true"] {{
    color: {PRIMARY};
}}

QFrame#card[affordable="false"] QLabel[role="name"],
QFrame#card[affordable="false"] QLabel[role="secondary"] {{
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
    padding: 6px 10px;
}}

QLabel#creditText {{
    color: {TEXT_PRIMARY};
    font-size: 19px;
    font-weight: 700;
}}

QLabel#creditText[warning="true"] {{
    color: {ERROR};
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
    border: 2px solid {PRIMARY};
    border-radius: 16px;
    text-align: center;
    background: {SURFACE};
    color: {TEXT_PRIMARY};
}}

QProgressBar#processProgress::chunk {{
    background: {ACCENT_PINK};
    border-radius: 12px;
}}

QPushButton#confirmButton {{
    min-height: 45px;
    color: {SURFACE};
    border: none;
    border-radius: 12px;
    padding: 0 20px;
    font-size: 17px;
    font-weight: 700;
    background:qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {PRIMARY},
        stop:1 {PRIMARY_HOVER}
    );
}}

QPushButton#confirmButton:hover {{
    background:qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {PRIMARY_HOVER},
        stop:1 {ORANGE}
    );
}}

QPushButton#confirmButton:pressed {{
    background:qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {PRIMARY_DARK},
        stop:1 {PRIMARY_HOVER}
    );
    padding-top: 2px;
}}

QPushButton#confirmButton:disabled {{
    background: #cbd5e1;
    color: #94a3b8;
}}

QFrame#instructionsPanel {{
    background-color: #f1f5f9;
    border: 1px solid {BORDER};
    border-radius: 18px;
}}

QFrame#instructionStep {{
    background: transparent;
}}

QLabel#heroImage {{
    background-color: #fff7fb;
    border: 1px solid #fbcfe8;
    border-radius: 18px;
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
