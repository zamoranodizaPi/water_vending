"""Instruction and message screens with persistent branding header."""
from __future__ import annotations

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QFrame

APP_FONT = "'Spicy Rice','DejaVu Sans'"
HEADER_STYLE = "QFrame{background:#0d6efd; border-radius:20px;}"
SCREEN_BG = "QWidget { background:#f3f7fb; }"
PRIMARY_TITLE_STYLE = f"font-family:{APP_FONT}; font-size:48px; font-weight:800; color:#ffffff;"
SECTION_TITLE_STYLE = f"font-family:{APP_FONT}; font-size:32px; font-weight:900; color:#0d6efd;"
BODY_TEXT_STYLE = f"font-family:{APP_FONT}; font-size:20px; font-weight:500; color:#1f2937;"
PRIMARY_BUTTON_STYLE = (
    f"QPushButton{{font-family:{APP_FONT}; font-size:22px; font-weight:800; background:#0d6efd; color:white; "
    "border-radius:16px; border:none; padding:8px 20px;}}"
    "QPushButton:hover{background:#0b5ed7;}"
    "QPushButton:disabled{background:#9ca3af; color:#e5e7eb;}"
)


class BrandedScreen(QWidget):
    def __init__(self, logo_path):
        super().__init__()
        self.setStyleSheet(SCREEN_BG)
        self.logo_path = logo_path
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(14, 10, 14, 10)
        self.root.setSpacing(0)
        self._build_header()

    def _build_header(self):
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(82)
        self.header_frame.setStyleSheet(HEADER_STYLE)
        title_row = QHBoxLayout(self.header_frame)
        title_row.setContentsMargins(20, 10, 20, 10)
        title_row.setSpacing(12)

        self.logo = QLabel(self.header_frame)
        self.logo.setFixedSize(920, 82)
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("background: transparent;")
        pix = QPixmap(str(self.logo_path)).scaled(900, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:#ffffff;")
        else:
            self.logo.setPixmap(pix)
        title_row.addWidget(self.logo, 1, Qt.AlignCenter)
        self.root.addWidget(self.header_frame)

    def set_credit(self, credit: float):
        return

class PromptScreen(BrandedScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.ok_pressed = QPushButton("OK")
        self._movie = None
        self._footer_hint_base = "Presione OK cuando este listo"
        self._build_ui()

    def _build_ui(self):
        self.title = QLabel("Instrucción")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(SECTION_TITLE_STYLE)

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setFixedHeight(190)

        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet(BODY_TEXT_STYLE)
        self.subtitle.setWordWrap(True)

        self.footer_hint = QLabel(self._footer_hint_base)
        self.footer_hint.setAlignment(Qt.AlignCenter)
        self.footer_hint.setStyleSheet(BODY_TEXT_STYLE)
        self.footer_hint.setWordWrap(True)

        self.ok_pressed.setMinimumHeight(56)
        self.ok_pressed.setMinimumWidth(250)
        self.ok_pressed.setMaximumWidth(340)
        self.ok_pressed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ok_pressed.setStyleSheet(PRIMARY_BUTTON_STYLE)

        self.root.addSpacing(12)
        self.root.addWidget(self.title)
        self.root.addSpacing(10)
        self.root.addWidget(self.image)
        self.root.addSpacing(16)
        self.root.addWidget(self.subtitle)
        self.root.addSpacing(10)
        self.root.addWidget(self.footer_hint)
        self.root.addSpacing(14)
        self.root.addWidget(self.ok_pressed, alignment=Qt.AlignCenter)
        self.root.addStretch()

    def set_prompt_countdown(self, seconds: int | None):
        if seconds is None:
            self.footer_hint.setText(self._footer_hint_base)
            return
        self.footer_hint.setText(f"{self._footer_hint_base} ({seconds})")

    def configure(self, title: str, image_path, subtitle: str, image_size=None):
        self.title.setText(title)
        self.image.setMovie(None)
        self._movie = None
        if str(image_path).lower().endswith(".gif"):
            self._movie = QMovie(str(image_path))
            if self._movie.isValid():
                self.image.setMovie(self._movie)
                self._movie.start()
            else:
                self.image.setText("[Animación no disponible]")
                self.image.setStyleSheet("font-size:25px; color:#64748b;")
        else:
            width, height = image_size or (300, 190)
            pix = QPixmap(str(image_path)).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if pix.isNull():
                self.image.setText("[Imagen no disponible]")
                self.image.setStyleSheet("font-size:25px; color:#64748b;")
            else:
                self.image.setPixmap(pix)
                self.image.setStyleSheet("")
        self.subtitle.setText(subtitle)


class MessageScreen(BrandedScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self._movie = None
        self.message = QLabel("")
        self.animation = QLabel()
        self._build_ui()

    def _build_ui(self):
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setStyleSheet(SECTION_TITLE_STYLE)
        self.message.setWordWrap(True)
        self.animation.setAlignment(Qt.AlignCenter)
        self.animation.setFixedHeight(170)

        self.root.addSpacing(18)
        self.root.addWidget(self.message)
        self.root.addSpacing(14)
        self.root.addWidget(self.animation)
        self.root.addStretch()

    def set_message(self, text: str, gif_path=None, image_path=None, image_size=None):
        self.message.setText(text)
        self.animation.clear()
        self.animation.setMovie(None)
        self._movie = None
        if image_path:
            width, height = image_size or (170, 150)
            pix = QPixmap(str(image_path)).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if pix.isNull():
                self.animation.setText("[Imagen no disponible]")
                self.animation.setStyleSheet("font-size:22px; color:#64748b;")
            else:
                self.animation.setPixmap(pix)
                self.animation.setStyleSheet("")
        elif gif_path:
            self._movie = QMovie(str(gif_path))
            if self._movie.isValid():
                if image_size:
                    self._movie.setScaledSize(QSize(*image_size))
                self.animation.setMovie(self._movie)
                self._movie.start()
            else:
                self.animation.setText("[Animación no disponible]")
                self.animation.setStyleSheet("font-size:22px; color:#64748b;")
