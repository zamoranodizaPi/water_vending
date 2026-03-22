"""Instruction and message screens with persistent branding header."""
from __future__ import annotations

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QFrame

from theme import APP_FONT, PRIMARY, refresh_style


class BrandedScreen(QWidget):
    def __init__(self, logo_path):
        super().__init__()
        self.setObjectName("screen")
        self.logo_path = logo_path
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(14, 10, 14, 10)
        self.root.setSpacing(0)
        self._build_header()

    def _build_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header")
        self.header_frame.setFixedHeight(78)
        title_row = QHBoxLayout(self.header_frame)
        title_row.setContentsMargins(18, 10, 18, 10)
        title_row.setSpacing(12)

        self.logo = QLabel(self.header_frame)
        self.logo.setObjectName("logoLabel")
        self.logo.setFixedSize(150, 54)
        self.logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        pix = QPixmap(str(self.logo_path)).scaled(140, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:{PRIMARY};")
        else:
            self.logo.setPixmap(pix)

        self.header_title = QLabel("Agua Purificada Lupita")
        self.header_title.setObjectName("headerTitle")
        self.header_title.setAlignment(Qt.AlignCenter)

        title_row.addWidget(self.logo, 0, Qt.AlignVCenter)
        title_row.addStretch()
        title_row.addWidget(self.header_title, 0, Qt.AlignCenter)
        title_row.addStretch()

        spacer = QWidget(self.header_frame)
        spacer.setFixedWidth(150)
        title_row.addWidget(spacer, 0, Qt.AlignVCenter)
        self.root.addWidget(self.header_frame)

    def set_credit(self, credit: float):
        return

class PromptScreen(BrandedScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.setObjectName("promptScreen")
        self.ok_pressed = QPushButton("OK")
        self._movie = None
        self._footer_hint_base = "Presione OK cuando este listo"
        self._build_ui()

    def _build_ui(self):
        self.title = QLabel("Instrucción")
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setFixedHeight(190)

        self.subtitle = QLabel("")
        self.subtitle.setObjectName("bodyText")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)

        self.footer_hint = QLabel(self._footer_hint_base)
        self.footer_hint.setObjectName("bodyText")
        self.footer_hint.setProperty("role", "secondary")
        self.footer_hint.setAlignment(Qt.AlignCenter)
        self.footer_hint.setWordWrap(True)

        self.ok_pressed.setProperty("variant", "primary")
        self.ok_pressed.setMinimumHeight(56)
        self.ok_pressed.setMinimumWidth(250)
        self.ok_pressed.setMaximumWidth(340)
        self.ok_pressed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ok_pressed.setStyleSheet(f"QPushButton{{font-family:{APP_FONT}; font-size:22px;}}")

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
                self.image.setProperty("role", "secondary")
                self.image.setStyleSheet("font-size:25px;")
                refresh_style(self.image)
        else:
            width, height = image_size or (300, 190)
            pix = QPixmap(str(image_path)).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if pix.isNull():
                self.image.setText("[Imagen no disponible]")
                self.image.setProperty("role", "secondary")
                self.image.setStyleSheet("font-size:25px;")
                refresh_style(self.image)
            else:
                self.image.setPixmap(pix)
                self.image.setProperty("role", "")
                self.image.setStyleSheet("")
                refresh_style(self.image)
        self.subtitle.setText(subtitle)


class MessageScreen(BrandedScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.setObjectName("messageScreen")
        self._movie = None
        self.message = QLabel("")
        self.animation = QLabel()
        self._build_ui()

    def _build_ui(self):
        self.message.setObjectName("screenTitle")
        self.message.setAlignment(Qt.AlignCenter)
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
                self.animation.setProperty("role", "secondary")
                self.animation.setStyleSheet("font-size:22px;")
                refresh_style(self.animation)
            else:
                self.animation.setPixmap(pix)
                self.animation.setProperty("role", "")
                self.animation.setStyleSheet("")
                refresh_style(self.animation)
        elif gif_path:
            self._movie = QMovie(str(gif_path))
            if self._movie.isValid():
                if image_size:
                    self._movie.setScaledSize(QSize(*image_size))
                self.animation.setMovie(self._movie)
                self._movie.start()
            else:
                self.animation.setText("[Animación no disponible]")
                self.animation.setProperty("role", "secondary")
                self.animation.setStyleSheet("font-size:22px;")
                refresh_style(self.animation)
