"""Dynamic glass-style theme system for the water vending touchscreen UI."""
from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation
from PyQt5.QtGui import QColor

from config import settings

APP_FONT = "'DejaVu Sans','Liberation Sans','Noto Sans','Sans Serif'"


class ThemeManager:
    current_theme = settings.UI_THEME
    current_mode = settings.UI_MODE

    THEMES = {
        "arcade_mario": {
            "light": {
                "background": ("#00AEEF", "#7EDBFF", "#FFD700"),
                "card_color": (255, 246, 214),
                "primary": "#FF0000",
                "secondary": "#00AEEF",
                "accent": "#00FF00",
                "text": "#2b1608",
                "text_secondary": "#8B4513",
                "price": "#c40000",
                "button_gradient": ("#FF0000", "#FFD700", "#00AEEF"),
                "glass_opacity": 0.82,
            },
            "dark": {
                "background": ("#13284f", "#1e3a6b", "#8B4513"),
                "card_color": (31, 24, 18),
                "primary": "#FF4D4D",
                "secondary": "#4DD7FF",
                "accent": "#FFD700",
                "text": "#FFF6D6",
                "text_secondary": "#FFD56A",
                "price": "#FFD700",
                "button_gradient": ("#FF0000", "#00AEEF", "#FFD700"),
                "glass_opacity": 0.34,
            },
        },
        "blue_ocean": {
            "light": {
                "background": ("#dbeafe", "#eff6ff", "#fde68a"),
                "card_color": (255, 255, 255),
                "primary": "#2563eb",
                "secondary": "#0f766e",
                "accent": "#facc15",
                "text": "#0f172a",
                "text_secondary": "#334155",
                "price": "#1d4ed8",
                "button_gradient": ("#2563eb", "#0ea5e9", "#facc15"),
                "glass_opacity": 0.72,
            },
            "dark": {
                "background": ("#020617", "#0f172a", "#1d4ed8"),
                "card_color": (15, 23, 42),
                "primary": "#60a5fa",
                "secondary": "#22d3ee",
                "accent": "#facc15",
                "text": "#e2e8f0",
                "text_secondary": "#cbd5e1",
                "price": "#93c5fd",
                "button_gradient": ("#1d4ed8", "#2563eb", "#facc15"),
                "glass_opacity": 0.24,
            },
        },
        "yellow_industrial": {
            "light": {
                "background": ("#fff7ed", "#fef3c7", "#fde68a"),
                "card_color": (255, 251, 235),
                "primary": "#ca8a04",
                "secondary": "#92400e",
                "accent": "#f97316",
                "text": "#1f2937",
                "text_secondary": "#57534e",
                "price": "#a16207",
                "button_gradient": ("#facc15", "#f59e0b", "#f97316"),
                "glass_opacity": 0.7,
            },
            "dark": {
                "background": ("#1c1917", "#292524", "#78350f"),
                "card_color": (41, 37, 36),
                "primary": "#facc15",
                "secondary": "#fb923c",
                "accent": "#f97316",
                "text": "#fafaf9",
                "text_secondary": "#e7e5e4",
                "price": "#fde68a",
                "button_gradient": ("#ca8a04", "#ea580c", "#facc15"),
                "glass_opacity": 0.28,
            },
        },
        "green_nature": {
            "light": {
                "background": ("#dcfce7", "#ecfdf5", "#bef264"),
                "card_color": (255, 255, 255),
                "primary": "#16a34a",
                "secondary": "#0f766e",
                "accent": "#84cc16",
                "text": "#14532d",
                "text_secondary": "#3f6212",
                "price": "#15803d",
                "button_gradient": ("#16a34a", "#22c55e", "#84cc16"),
                "glass_opacity": 0.68,
            },
            "dark": {
                "background": ("#052e16", "#14532d", "#166534"),
                "card_color": (20, 83, 45),
                "primary": "#4ade80",
                "secondary": "#2dd4bf",
                "accent": "#a3e635",
                "text": "#ecfdf5",
                "text_secondary": "#d9f99d",
                "price": "#86efac",
                "button_gradient": ("#166534", "#16a34a", "#84cc16"),
                "glass_opacity": 0.26,
            },
        },
        "sunset_energy": {
            "light": {
                "background": ("#fff1f2", "#ffe4e6", "#fed7aa"),
                "card_color": (255, 255, 255),
                "primary": "#ec4899",
                "secondary": "#f43f5e",
                "accent": "#ff6b35",
                "text": "#111827",
                "text_secondary": "#64748b",
                "price": "#f43f5e",
                "button_gradient": ("#ec4899", "#f43f5e", "#ff6b35"),
                "glass_opacity": 0.7,
            },
            "dark": {
                "background": ("#1f1020", "#3b1020", "#7c2d12"),
                "card_color": (49, 18, 33),
                "primary": "#f472b6",
                "secondary": "#fb7185",
                "accent": "#fb923c",
                "text": "#fff7ed",
                "text_secondary": "#fecdd3",
                "price": "#fda4af",
                "button_gradient": ("#db2777", "#e11d48", "#f97316"),
                "glass_opacity": 0.26,
            },
        },
        "purple_modern": {
            "light": {
                "background": ("#f5f3ff", "#eef2ff", "#ddd6fe"),
                "card_color": (255, 255, 255),
                "primary": "#7c3aed",
                "secondary": "#8b5cf6",
                "accent": "#06b6d4",
                "text": "#1e1b4b",
                "text_secondary": "#5b21b6",
                "price": "#6d28d9",
                "button_gradient": ("#7c3aed", "#8b5cf6", "#06b6d4"),
                "glass_opacity": 0.7,
            },
            "dark": {
                "background": ("#0f0722", "#1e1b4b", "#312e81"),
                "card_color": (30, 27, 75),
                "primary": "#a78bfa",
                "secondary": "#c084fc",
                "accent": "#22d3ee",
                "text": "#f5f3ff",
                "text_secondary": "#ddd6fe",
                "price": "#c4b5fd",
                "button_gradient": ("#6d28d9", "#7c3aed", "#06b6d4"),
                "glass_opacity": 0.26,
            },
        },
        "black_gold": {
            "light": {
                "background": ("#0B0B0B", "#050505", "#1A1A1A"),
                "card_color": "#1A1A1A",
                "primary": "#D4AF37",
                "secondary": "#C9A227",
                "accent": "#F5D76E",
                "text": "#E5E5E5",
                "text_secondary": "#A3A3A3",
                "price": "#FFD700",
                "border": "rgba(212, 175, 55, 0.25)",
                "button_gradient": ("#D4AF37", "#B8962E", "#F5D76E"),
                "glass_opacity": 0.05,
            },
            "dark": {
                "background": ("#050505", "#050505", "#1A1A1A"),
                "card_color": "#121212",
                "primary": "#FFD700",
                "secondary": "#D4AF37",
                "accent": "#FACC15",
                "text": "#FAFAFA",
                "text_secondary": "#9CA3AF",
                "price": "#FFD700",
                "border": "rgba(255, 215, 0, 0.3)",
                "button_gradient": ("#FFD700", "#C9A227", "#B8962E"),
                "glass_opacity": 0.03,
            },
        },
    }

    @classmethod
    def sync_from_settings(cls) -> None:
        cls.current_theme = settings.UI_THEME if settings.UI_THEME in cls.THEMES else "sunset_energy"
        cls.current_mode = settings.UI_MODE if settings.UI_MODE in settings.AVAILABLE_MODES else "light"

    @classmethod
    def get_theme(cls) -> dict:
        cls.sync_from_settings()
        return cls.THEMES[cls.current_theme][cls.current_mode]


def rgba_from_rgb(rgb: tuple[int, int, int], opacity: float) -> str:
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity:.3f})"


def _rgb_tuple(color: str | tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(color, tuple):
        return color
    parsed = QColor(color)
    return parsed.red(), parsed.green(), parsed.blue()


def _mix(color_a: str, color_b: str, factor: float) -> str:
    left = QColor(color_a)
    right = QColor(color_b)
    red = int(left.red() + (right.red() - left.red()) * factor)
    green = int(left.green() + (right.green() - left.green()) * factor)
    blue = int(left.blue() + (right.blue() - left.blue()) * factor)
    return QColor(red, green, blue).name()


def _refresh_exports() -> dict:
    palette = ThemeManager.get_theme()
    card_text = _mix(palette["primary"], "#000000", 0.28) if ThemeManager.current_mode == "light" else _mix(palette["primary"], "#ffffff", 0.24)
    card_meta = _mix(palette["primary"], "#ffffff", 0.22) if ThemeManager.current_mode == "light" else _mix(palette["primary"], "#ffffff", 0.5)
    card_rgb = _rgb_tuple(palette["card_color"])
    border = palette.get("border") or rgba_from_rgb((255, 255, 255), 0.28 if ThemeManager.current_mode == "light" else 0.18)
    globals().update(
        {
            "PRIMARY": palette["primary"],
            "PRIMARY_HOVER": _mix(palette["primary"], "#ffffff", 0.18),
            "PRIMARY_DARK": _mix(palette["primary"], "#000000", 0.22),
            "ORANGE": palette["accent"],
            "ACCENT": palette["accent"],
            "ACCENT_LIGHT": _mix(palette["accent"], "#ffffff", 0.78),
            "ACCENT_ORANGE": palette["accent"],
            "ACCENT_PINK": palette["secondary"],
            "BACKGROUND": palette["background"][1],
            "SURFACE": rgba_from_rgb(card_rgb, min(0.96, palette["glass_opacity"] + 0.18)),
            "TEXT_PRIMARY": palette["text"],
            "TEXT_SECONDARY": palette["text_secondary"],
            "SECONDARY": palette["text_secondary"],
            "BORDER": border,
            "ERROR": "#ef4444",
            "ERROR_BG": "rgba(239, 68, 68, 0.14)",
            "CREDIT_BG": rgba_from_rgb(card_rgb, min(0.9, palette["glass_opacity"] + 0.1)),
            "CARD_TEXT_STRONG": card_text,
            "CARD_TEXT_META": card_meta,
        }
    )
    return palette


def build_stylesheet() -> str:
    palette = _refresh_exports()
    bg0, bg1, bg2 = palette["background"]
    card_rgb = _rgb_tuple(palette["card_color"])
    glass = rgba_from_rgb(card_rgb, palette["glass_opacity"])
    glass_high = rgba_from_rgb(card_rgb, min(0.92, palette["glass_opacity"] + 0.12))
    glass_soft = rgba_from_rgb(card_rgb, max(0.14, palette["glass_opacity"] - 0.22))
    black_gold_mode = ThemeManager.current_theme == "black_gold"
    bright_border = palette.get("border") or ("rgba(255, 255, 255, 0.42)" if ThemeManager.current_mode == "light" else "rgba(255, 255, 255, 0.18)")
    dim_border = "rgba(212, 175, 55, 0.14)" if black_gold_mode else ("rgba(255, 255, 255, 0.22)" if ThemeManager.current_mode == "light" else "rgba(255, 255, 255, 0.12)")
    shadow = "rgba(15, 23, 42, 0.22)" if ThemeManager.current_mode == "light" else "rgba(2, 6, 23, 0.42)"
    hero_bg = rgba_from_rgb(card_rgb, min(0.84, palette["glass_opacity"] + 0.08))
    progress_bg = rgba_from_rgb(card_rgb, min(0.9, palette["glass_opacity"] + 0.14))
    button0, button1, button2 = palette["button_gradient"]
    button_pressed0 = "#A16207" if black_gold_mode else _mix(button0, "#000000", 0.12)
    button_pressed1 = "#A16207" if black_gold_mode else _mix(button1, "#000000", 0.12)
    button_pressed2 = "#A16207" if black_gold_mode else _mix(button2, "#000000", 0.12)
    disabled_bg = rgba_from_rgb((148, 163, 184), 0.35)
    disabled_text = "rgba(255, 255, 255, 0.6)" if ThemeManager.current_mode == "dark" else "#94a3b8"
    arcade_mode = ThemeManager.current_theme == "arcade_mario"
    panel_radius = 10 if arcade_mode else 22
    card_radius = 12 if arcade_mode else 24
    button_radius = 8 if arcade_mode else 16
    card_border = "rgba(255, 255, 255, 0.28)" if arcade_mode else bright_border
    hover_border = "rgba(255, 215, 0, 0.46)" if black_gold_mode else bright_border
    selected_border = "#FFD700" if black_gold_mode else "rgba(255, 255, 255, 0.68)"
    attention_border = "#FFD700" if black_gold_mode else button2
    button_text = "#050505" if black_gold_mode else "white"
    alert_bg = "rgba(212, 175, 55, 0.12)" if black_gold_mode else "rgba(255, 255, 255, 0.28)"
    credit_bg = "rgba(10, 10, 10, 0.92)" if black_gold_mode else glass
    credit_flash_bg = "rgba(24, 24, 24, 0.96)" if black_gold_mode else rgba_from_rgb(card_rgb, min(0.96, palette["glass_opacity"] + 0.18))
    background_overlay = """
    background-image:
      linear-gradient(0deg, transparent 24%, rgba(255,255,255,0.12) 25%, rgba(255,255,255,0.12) 26%, transparent 27%, transparent 74%, rgba(255,255,255,0.12) 75%, rgba(255,255,255,0.12) 76%, transparent 77%, transparent),
      linear-gradient(90deg, transparent 24%, rgba(255,255,255,0.12) 25%, rgba(255,255,255,0.12) 26%, transparent 27%, transparent 74%, rgba(255,255,255,0.12) 75%, rgba(255,255,255,0.12) 76%, transparent 77%, transparent);
    background-size: 24px 24px;
    """ if arcade_mode else ""

    return f"""
QWidget {{
    background: transparent;
    color: {TEXT_PRIMARY};
    font-family: {APP_FONT};
}}

QStackedWidget,
QWidget#screen,
QWidget#productScreen,
QWidget#promptScreen,
QWidget#messageScreen,
QWidget#dispensingScreen,
QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {bg0},
        stop:0.5 {bg1},
        stop:1 {bg2}
    );
    {background_overlay}
}}

QFrame#modernHeader,
QFrame#contentPanel,
QFrame#instructionsPanel,
QFrame#creditPill,
QFrame#actionBox,
QFrame#productCard,
QFrame#card {{
    background: {"rgba(255, 255, 255, 0.03)" if black_gold_mode else f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {glass_high}, stop:1 {glass})"};
    border: {3 if arcade_mode else (1 if black_gold_mode else 1)}px solid {card_border};
    border-radius: {18 if black_gold_mode else panel_radius}px;
}}

QFrame#modernHeader {{
    background: {"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,0.04), stop:1 rgba(255,255,255,0.02))" if black_gold_mode else f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {button0}, stop:0.55 {button1}, stop:1 {button2})"};
    border: {4 if arcade_mode else 1}px solid {"rgba(212, 175, 55, 0.22)" if black_gold_mode else "rgba(255, 255, 255, 0.32)"};
}}

QFrame#creditPill {{
    border-radius: {18 if black_gold_mode else panel_radius}px;
    background: {credit_bg};
}}

QFrame#creditPill[flash="true"] {{
    border: 2px solid {attention_border};
    background: {credit_flash_bg};
}}

QFrame#contentPanel[thankyou="true"] {{
    background: transparent;
    border: none;
}}

QFrame#productCard,
QFrame#card {{
    border-radius: {18 if black_gold_mode else card_radius}px;
}}

QFrame#productCard[selected="true"],
QFrame#card[selected="true"] {{
    border: 2px solid {selected_border};
}}

QFrame#productCard[attention="true"],
QFrame#card[attention="true"] {{
    border: 2px solid {attention_border};
}}

QFrame#productCard[hovered="true"],
QFrame#card[hovered="true"] {{
    border: 1px solid {hover_border};
    background: {"rgba(255, 255, 255, 0.05)" if black_gold_mode else f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {glass_high}, stop:1 {glass})"};
}}

QFrame#productCard[affordable="false"],
QFrame#card[affordable="false"] {{
    background: {glass_soft};
    border: 1px solid {dim_border};
}}

QLabel {{
    background: transparent;
    color: {TEXT_PRIMARY};
}}

QLabel#headerTitle {{
    color: {"#FAFAFA" if black_gold_mode else "rgba(255, 255, 255, 0.98)"};
    font-size: 27px;
    font-weight: 800;
}}

QLabel#headerSubtitle {{
    color: {"#A3A3A3" if black_gold_mode else "rgba(255, 255, 255, 0.82)"};
    font-size: 12px;
    font-weight: 600;
}}

QLabel#screenTitle {{
    color: {TEXT_PRIMARY};
    font-size: 30px;
    font-weight: 800;
}}

QLabel#bodyText {{
    color: {TEXT_PRIMARY};
    font-size: 19px;
    font-weight: 600;
}}

QLabel#sectionLabel {{
    color: {TEXT_PRIMARY};
    font-size: 20px;
    font-weight: 800;
}}

QLabel#sectionLabel[warning="true"] {{
    color: {ORANGE};
}}

QLabel#alertLabel {{
    color: {TEXT_PRIMARY};
    background: {alert_bg};
    border: 1px solid {bright_border};
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    padding: 8px 12px;
}}

QLabel#selectionCountdown {{
    color: {PRIMARY};
    font-size: 18px;
    font-weight: 800;
}}

QLabel#creditText {{
    color: {palette["price"] if black_gold_mode else TEXT_PRIMARY};
    font-size: 23px;
    font-weight: 800;
}}

QLabel#creditText[warning="true"] {{
    color: {ORANGE};
}}

QLabel[role="secondary"],
QLabel#footerHint,
QLabel#statusHint {{
    color: {TEXT_SECONDARY};
}}

QLabel[role="warning"] {{
    color: {ERROR};
}}

QLabel[role="price"] {{
    color: {palette["price"]};
    font-size: 30px;
    font-weight: 900;
}}

QLabel#productPrice {{
    color: {CARD_TEXT_STRONG};
    font-size: 30px;
    font-weight: 900;
}}

QLabel#productPriceCorner {{
    color: {CARD_TEXT_META};
    font-size: 24px;
    font-weight: 900;
}}

QLabel#productVolume {{
    color: {CARD_TEXT_META};
    font-size: 15px;
    font-weight: 800;
}}

QLabel#productFallback,
QLabel#imageFallback {{
    color: rgba(255, 255, 255, 0.92);
    font-size: 22px;
    font-weight: 800;
}}

QPushButton[variant="primary"],
QPushButton#confirmButton,
QPushButton#buyButton {{
    color: {button_text};
    border: {4 if arcade_mode else 1}px solid rgba(255, 255, 255, 0.2);
    border-radius: {14 if black_gold_mode else button_radius}px;
    padding: {12 if black_gold_mode else 10}px 18px;
    font-size: 18px;
    font-weight: 800;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {button0},
        stop:0.55 {button1},
        stop:1 {button2}
    );
}}

QPushButton#buyButton {{
    min-height: 22px;
    font-size: 19px;
    border-radius: {button_radius}px;
}}

QPushButton[variant="primary"]:hover,
QPushButton#confirmButton:hover,
QPushButton#buyButton:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {"#FACC15" if black_gold_mode else _mix(button0, "#ffffff", 0.08)},
        stop:0.55 {"#D4AF37" if black_gold_mode else _mix(button1, "#ffffff", 0.08)},
        stop:1 {_mix(button2, "#ffffff", 0.08)}
    );
}}

QPushButton[variant="primary"]:pressed,
QPushButton#confirmButton:pressed,
QPushButton#buyButton:pressed {{
    padding-top: 12px;
    padding-bottom: 8px;
    background: {"#A16207" if black_gold_mode else f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {button_pressed0}, stop:0.55 {button_pressed1}, stop:1 {button_pressed2})"};
}}

QPushButton[variant="primary"]:disabled,
QPushButton#confirmButton:disabled,
QPushButton#buyButton:disabled {{
    background: {disabled_bg};
    color: {disabled_text};
    border: 1px solid {dim_border};
}}

QPushButton[variant="secondary"] {{
    background: rgba(255, 255, 255, 0.18);
    color: {TEXT_PRIMARY};
    border: 1px solid {bright_border};
    border-radius: 16px;
    font-size: 18px;
    font-weight: 800;
    padding: 10px 18px;
}}

QPushButton[variant="secondary"]:hover {{
    background: rgba(255, 255, 255, 0.26);
}}

QPushButton[variant="secondary"]:pressed {{
    background: rgba(255, 255, 255, 0.2);
}}

QProgressBar#processProgress {{
    font-size: 22px;
    font-weight: 800;
    text-align: center;
    color: {TEXT_PRIMARY};
    background: {progress_bg};
    border: 1px solid {bright_border};
    border-radius: 18px;
}}

QProgressBar#processProgress::chunk {{
    border-radius: 14px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {button0},
        stop:1 {button2}
    );
}}

QLabel#heroImage {{
    background: {hero_bg};
    border: 1px solid {bright_border};
    border-radius: 22px;
}}

QFrame#instructionStep {{
    background: rgba(255, 255, 255, 0.08);
    border-radius: 18px;
}}

QTableWidget,
QTextEdit {{
    background: {glass};
    color: {TEXT_PRIMARY};
    border: 1px solid {bright_border};
    border-radius: 18px;
    gridline-color: {dim_border};
    selection-background-color: {PRIMARY};
    selection-color: white;
}}
"""


GLOBAL_STYLESHEET = build_stylesheet()


def _animate_theme_change(app) -> None:
    window = app.activeWindow()
    if window is None or not window.isVisible():
        return
    try:
        window.setWindowOpacity(0.96)
        animation = QPropertyAnimation(window, b"windowOpacity", window)
        animation.setDuration(180)
        animation.setStartValue(0.96)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        window._theme_animation = animation
    except Exception:
        return


def apply_app_theme(app) -> None:
    global GLOBAL_STYLESHEET
    GLOBAL_STYLESHEET = build_stylesheet()
    app.setStyleSheet(GLOBAL_STYLESHEET)
    _animate_theme_change(app)


def refresh_style(widget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def color_with_alpha(hex_color: str, alpha: int) -> QColor:
    color = QColor(hex_color)
    color.setAlpha(alpha)
    return color


_refresh_exports()
