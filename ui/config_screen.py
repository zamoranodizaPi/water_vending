"""Configuration flow screens for physical-button navigation."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from config import settings
import theme
from theme import refresh_style

HEADER_HEIGHT = 90
CONFIG_TITLE = "Modo configuración"


class ConfigBaseScreen(QWidget):
    def __init__(self, logo_path):
        super().__init__()
        self.logo_path = logo_path
        self.setObjectName("screen")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self.header = QFrame()
        self.header.setObjectName("modernHeader")
        self.header.setFixedHeight(HEADER_HEIGHT)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(16, 10, 16, 10)
        header_layout.setSpacing(0)

        icon = QLabel()
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(72, 72)
        pix = QPixmap(str(self.logo_path))
        if pix.isNull():
            icon.setText("L")
            icon.setObjectName("imageFallback")
        else:
            icon.setPixmap(pix.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon, 0, Qt.AlignVCenter)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(0)
        title_col.addStretch(1)
        title = QLabel(settings.BRAND_TITLE)
        title.setObjectName("headerTitle")
        title_col.addWidget(title)
        subtitle = QLabel(settings.BRAND_TAGLINE)
        subtitle.setObjectName("headerSubtitle")
        title_col.addWidget(subtitle)
        title_col.addStretch(1)
        header_layout.addLayout(title_col, 1)
        root.addWidget(self.header)

        self.panel = QFrame()
        self.panel.setObjectName("contentPanel")
        self.panel_layout = QVBoxLayout(self.panel)
        self.panel_layout.setContentsMargins(24, 20, 24, 20)
        self.panel_layout.setSpacing(12)
        root.addWidget(self.panel, 1)


class ConfigHoldScreen(ConfigBaseScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.title = QLabel("Entrando a configuración...")
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.help_text = QLabel("Mantenga OK y Cancelar presionados durante 10 segundos")
        self.help_text.setObjectName("footerHint")
        self.help_text.setAlignment(Qt.AlignCenter)
        self.help_text.setWordWrap(True)

        self.progress = QProgressBar()
        self.progress.setObjectName("processProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(48)
        self.progress.setFixedWidth(520)

        self.panel_layout.addStretch(1)
        self.panel_layout.addWidget(self.title)
        self.panel_layout.addWidget(self.help_text)
        self.panel_layout.addSpacing(10)
        self.panel_layout.addWidget(self.progress, 0, Qt.AlignCenter)
        self.panel_layout.addStretch(1)

    def set_progress(self, percent: int):
        self.progress.setValue(max(0, min(100, percent)))


class ConfigCodeScreen(ConfigBaseScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.digits = ["0", "0", "0", "0"]
        self.cursor_index = 0

        self.title = QLabel("Ingrese código")
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.hint = QLabel("P1:+  P2:-  P3:siguiente  OK:confirmar")
        self.hint.setObjectName("footerHint")
        self.hint.setAlignment(Qt.AlignCenter)

        self.code_row = QHBoxLayout()
        self.code_row.setContentsMargins(0, 0, 0, 0)
        self.code_row.setSpacing(14)
        self.digit_labels = []
        for _ in range(4):
            label = QLabel("_")
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(74, 90)
            self.digit_labels.append(label)
            self.code_row.addWidget(label)

        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setObjectName("bodyText")

        self.panel_layout.addStretch(1)
        self.panel_layout.addWidget(self.title)
        self.panel_layout.addSpacing(10)
        self.panel_layout.addLayout(self.code_row)
        self.panel_layout.addSpacing(10)
        self.panel_layout.addWidget(self.message)
        self.panel_layout.addStretch(1)
        self.panel_layout.addWidget(self.hint)
        self._refresh_digits()

    def configure(self, title: str, message: str = "", digits: str = "0000"):
        self.title.setText(title)
        self.digits = list(digits[:4].ljust(4, "0"))
        self.cursor_index = 0
        self.show_info(message)
        self._refresh_digits()

    def _refresh_digits(self):
        for index, label in enumerate(self.digit_labels):
            selected = index == self.cursor_index
            border_color = theme.ACCENT_ORANGE if selected else "#cbd5e1"
            label.setText(self.digits[index])
            label.setStyleSheet(
                f"""
                font-family:{theme.APP_FONT};
                font-size:38px;
                font-weight:800;
                color:{theme.TEXT_PRIMARY};
                background-color:{theme.SURFACE};
                border:3px solid {border_color};
                border-radius:16px;
                """
            )

    def increment_digit(self):
        self.digits[self.cursor_index] = str((int(self.digits[self.cursor_index]) + 1) % 10)
        self._refresh_digits()

    def next_digit(self):
        self.cursor_index = min(3, self.cursor_index + 1)
        self._refresh_digits()

    def decrement_digit(self):
        self.digits[self.cursor_index] = str((int(self.digits[self.cursor_index]) - 1) % 10)
        self._refresh_digits()

    def code(self) -> str:
        return "".join(self.digits)

    def show_error(self, text: str):
        self.message.setText(text)
        self.message.setStyleSheet(f"font-family:{theme.APP_FONT}; font-size:18px; font-weight:700; color:#dc2626;")

    def show_info(self, text: str):
        self.message.setText(text)
        self.message.setStyleSheet(f"font-family:{theme.APP_FONT}; font-size:18px; font-weight:700; color:{theme.PRIMARY};")


class ConfigTextScreen(ConfigBaseScreen):
    CHARSET = list(" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóúÑñ0123456789.-_@+()")

    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.max_length = 24
        self.active_length = 18
        self.empty_value = "Producto"
        self.characters = [" "] * self.max_length
        self.cursor_index = 0

        self.title = QLabel(CONFIG_TITLE)
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("")
        self.subtitle.setObjectName("bodyText")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)

        self.row = QHBoxLayout()
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(3)
        self.char_labels = []
        for _ in range(self.max_length):
            label = QLabel(" ")
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(30, 52)
            self.char_labels.append(label)
            self.row.addWidget(label)

        self.help = QLabel("P1:+  P2:-  P3:siguiente  OK:guardar  Cancelar:volver")
        self.help.setObjectName("footerHint")
        self.help.setAlignment(Qt.AlignCenter)
        self.help.setWordWrap(True)

        self.panel_layout.addWidget(self.title)
        self.panel_layout.addWidget(self.subtitle)
        self.panel_layout.addStretch(1)
        self.panel_layout.addLayout(self.row)
        self.panel_layout.addStretch(1)
        self.panel_layout.addWidget(self.help)
        self._refresh()

    def configure(
        self,
        title: str,
        subtitle: str,
        value: str,
        *,
        max_length: int = 18,
        empty_value: str = "Producto",
    ):
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.active_length = max(1, min(max_length, self.max_length))
        self.empty_value = empty_value
        text = (value or "")[: self.active_length].ljust(self.max_length)
        self.characters = list(text)
        self.cursor_index = 0
        self._refresh()

    def increment_char(self):
        current = self.characters[self.cursor_index]
        try:
            index = self.CHARSET.index(current)
        except ValueError:
            index = 0
        self.characters[self.cursor_index] = self.CHARSET[(index + 1) % len(self.CHARSET)]
        self._refresh()

    def next_char(self):
        self.cursor_index = (self.cursor_index + 1) % self.active_length
        self._refresh()

    def decrement_char(self):
        current = self.characters[self.cursor_index]
        try:
            index = self.CHARSET.index(current)
        except ValueError:
            index = 0
        self.characters[self.cursor_index] = self.CHARSET[(index - 1) % len(self.CHARSET)]
        self._refresh()

    def text(self) -> str:
        return "".join(self.characters[: self.active_length]).rstrip() or self.empty_value

    def _refresh(self):
        for index, label in enumerate(self.char_labels):
            visible = index < self.active_length
            label.setVisible(visible)
            if not visible:
                continue
            selected = index == self.cursor_index
            border_color = theme.ACCENT_ORANGE if selected else "#cbd5e1"
            background = theme.SURFACE if selected else "rgba(255, 255, 255, 0.16)"
            label.setText(self.characters[index] if self.characters[index] != " " else "·")
            label.setStyleSheet(
                f"""
                font-family:{theme.APP_FONT};
                font-size:24px;
                font-weight:800;
                color:{theme.TEXT_PRIMARY};
                background-color:{background};
                border:3px solid {border_color};
                border-radius:10px;
                """
            )


class ConfigMenuScreen(ConfigBaseScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.options = []
        self.index = 0
        self.title = QLabel(CONFIG_TITLE)
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)
        self.subtitle = QLabel("")
        self.subtitle.setObjectName("footerHint")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.hint = QLabel("P1:subir  P2:bajar  OK:seleccionar  Cancelar:volver")
        self.hint.setObjectName("footerHint")
        self.hint.setAlignment(Qt.AlignCenter)
        self.list_layout = QVBoxLayout()
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(6)
        self.items: list[tuple[QFrame, QLabel, QLabel]] = []

        self.panel_layout.addWidget(self.title)
        self.panel_layout.addWidget(self.subtitle)
        self.panel_layout.addSpacing(6)
        self.panel_layout.addLayout(self.list_layout, 1)
        self.panel_layout.addWidget(self.hint)

    def configure(self, title: str, subtitle: str, options: list[str], index: int = 0):
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.options = options
        self.index = index
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.items = []
        for option in options:
            frame = QFrame()
            frame.setObjectName("configMenuItem")
            frame.setFixedHeight(46)
            marker = QLabel("")
            marker.setFixedWidth(22)
            marker.setAlignment(Qt.AlignCenter)
            label = QLabel(option)
            label.setStyleSheet(f"font-family:{theme.APP_FONT}; font-size:22px; font-weight:700;")
            row = QHBoxLayout(frame)
            row.setContentsMargins(6, 4, 6, 4)
            row.setSpacing(8)
            row.addWidget(marker, 0)
            row.addWidget(label)
            self.items.append((frame, marker, label))
            self.list_layout.addWidget(frame)
        self._refresh()

    def move_up(self):
        self.index = (self.index - 1) % len(self.options)
        self._refresh()

    def move_down(self):
        self.index = (self.index + 1) % len(self.options)
        self._refresh()

    def current_option(self) -> str:
        return self.options[self.index]

    def _refresh(self):
        for index, (frame, marker, label) in enumerate(self.items):
            selected = index == self.index
            frame.setStyleSheet("background: transparent; border: none;")
            marker.setText("◆" if selected else "")
            marker.setStyleSheet(
                f"font-family:{theme.APP_FONT}; font-size:18px; font-weight:800; color:{theme.ACCENT_ORANGE if selected else theme.TEXT_PRIMARY};"
            )
            label.setStyleSheet(
                f"font-family:{theme.APP_FONT}; font-size:{24 if selected else 22}px; font-weight:{800 if selected else 700}; color:{theme.ACCENT_ORANGE if selected else theme.TEXT_PRIMARY};"
            )


class ConfigValueScreen(ConfigBaseScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.title = QLabel(CONFIG_TITLE)
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("")
        self.subtitle.setObjectName("bodyText")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)

        self.value = QLabel("")
        self.value.setProperty("role", "price")
        self.value.setAlignment(Qt.AlignCenter)

        self.help = QLabel("")
        self.help.setObjectName("footerHint")
        self.help.setAlignment(Qt.AlignCenter)
        self.help.setWordWrap(True)

        self.panel_layout.addStretch(1)
        self.panel_layout.addWidget(self.title)
        self.panel_layout.addWidget(self.subtitle)
        self.panel_layout.addSpacing(12)
        self.panel_layout.addWidget(self.value)
        self.panel_layout.addStretch(1)
        self.panel_layout.addWidget(self.help)

    def configure(self, title: str, subtitle: str, value: str, help_text: str):
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.value.setText(value)
        self.help.setText(help_text)
