"""Configuration flow screens for physical-button navigation."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from theme import ACCENT_ORANGE, APP_FONT, PRIMARY, SECONDARY, SURFACE, TEXT_PRIMARY, refresh_style

HEADER_HEIGHT = 90
TITLE_TEXT = "Agua Purificada Lupita"
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
        icon.setFixedSize(94, 94)
        pix = QPixmap(str(self.logo_path))
        if pix.isNull():
            icon.setText("L")
            icon.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:{SURFACE};")
        else:
            icon.setPixmap(pix.scaled(94, 94, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon, 0, Qt.AlignVCenter)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(0)
        title_col.addStretch(1)
        title = QLabel(TITLE_TEXT)
        title.setStyleSheet(f"font-family:{APP_FONT}; font-size:25px; font-weight:800; color:{SURFACE};")
        title_col.addWidget(title)
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

        self.help_text = QLabel("Mantenga OK y Garrafón presionados durante 10 segundos")
        self.help_text.setAlignment(Qt.AlignCenter)
        self.help_text.setWordWrap(True)
        self.help_text.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:18px; font-weight:600; color:{SECONDARY};"
        )

        self.progress = QProgressBar()
        self.progress.setObjectName("processProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(48)
        self.progress.setFixedWidth(520)
        self.progress.setStyleSheet(f"QProgressBar{{font-family:{APP_FONT};}}")

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

        self.hint = QLabel("P1:+  P2:siguiente  P3:anterior  OK:confirmar")
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:16px; font-weight:600; color:{SECONDARY};"
        )

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
        self.message.setStyleSheet(f"font-family:{APP_FONT}; font-size:18px; font-weight:700; color:{PRIMARY};")

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
            border_color = ACCENT_ORANGE if selected else "#cbd5e1"
            label.setText(self.digits[index])
            label.setStyleSheet(
                f"""
                font-family:{APP_FONT};
                font-size:38px;
                font-weight:800;
                color:{TEXT_PRIMARY};
                background-color:{SURFACE};
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

    def previous_digit(self):
        self.cursor_index = max(0, self.cursor_index - 1)
        self._refresh_digits()

    def code(self) -> str:
        return "".join(self.digits)

    def show_error(self, text: str):
        self.message.setText(text)
        self.message.setStyleSheet(f"font-family:{APP_FONT}; font-size:18px; font-weight:700; color:#dc2626;")

    def show_info(self, text: str):
        self.message.setText(text)
        self.message.setStyleSheet(f"font-family:{APP_FONT}; font-size:18px; font-weight:700; color:{PRIMARY};")


class ConfigMenuScreen(ConfigBaseScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.options = []
        self.index = 0
        self.title = QLabel(CONFIG_TITLE)
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)
        self.hint = QLabel("P1:subir  P2:bajar  P3:volver  OK:seleccionar")
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:16px; font-weight:600; color:{SECONDARY};"
        )
        self.list_layout = QVBoxLayout()
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)
        self.items = []

        self.panel_layout.addWidget(self.title)
        self.panel_layout.addSpacing(6)
        self.panel_layout.addLayout(self.list_layout, 1)
        self.panel_layout.addWidget(self.hint)

    def configure(self, options: list[str], index: int = 0):
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
            frame.setFixedHeight(56)
            label = QLabel(option)
            label.setStyleSheet(f"font-family:{APP_FONT}; font-size:22px; font-weight:700; color:{TEXT_PRIMARY};")
            row = QHBoxLayout(frame)
            row.setContentsMargins(18, 10, 18, 10)
            row.addWidget(label)
            self.items.append(frame)
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
        for index, frame in enumerate(self.items):
            selected = index == self.index
            frame.setStyleSheet(
                f"""
                background-color:{SURFACE};
                border:{'3px' if selected else '1px'} solid {ACCENT_ORANGE if selected else '#e2e8f0'};
                border-radius:16px;
                """
            )


class ConfigValueScreen(ConfigBaseScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.title = QLabel(CONFIG_TITLE)
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:18px; font-weight:600; color:{SECONDARY};"
        )

        self.value = QLabel("")
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:44px; font-weight:800; color:{PRIMARY};"
        )

        self.help = QLabel("")
        self.help.setAlignment(Qt.AlignCenter)
        self.help.setWordWrap(True)
        self.help.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:16px; font-weight:600; color:{SECONDARY};"
        )

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
