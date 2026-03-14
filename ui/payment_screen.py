"""Instruction and message screens with persistent branding header."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout


class BrandedScreen(QWidget):
    def __init__(self, logo_path):
        super().__init__()
        self.logo_path = logo_path
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(20, 12, 20, 12)
        self.root.setSpacing(10)
        self._build_header()

    def _build_header(self):
        row = QHBoxLayout()
        title1 = QLabel("Agua Purificada ")
        title1.setStyleSheet("font-size:46px; font-weight:800; color:#0e7490;")
        title2 = QLabel("Lupita")
        title2.setStyleSheet("font-size:50px; font-family:'Brush Script MT'; color:#ec4899;")
        logo = QLabel()
        logo.setFixedSize(132, 99)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(self.logo_path)).scaled(121, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            logo.setText("Lupita")
            logo.setStyleSheet("font-size:20px; color:#0e7490;")
        else:
            logo.setPixmap(pix)

        row.addStretch()
        row.addWidget(title1)
        row.addWidget(title2)
        row.addSpacing(16)
        row.addWidget(logo)
        row.addStretch()
        self.root.addLayout(row)


class PromptScreen(BrandedScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.ok_pressed = QPushButton("OK")
        self._movie = None
        self._build_ui()

    def _build_ui(self):
        self.title = QLabel("Instrucción")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:48px; font-weight:800; color:#0f766e;")

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setFixedHeight(290)

        self.subtitle = QLabel("")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("font-size:30px; color:#0f172a;")

        self.ok_pressed.setMinimumHeight(90)
        self.ok_pressed.setStyleSheet("font-size:42px; font-weight:800; background:#10b981; color:white; border-radius:14px;")

        self.root.addStretch()
        self.root.addWidget(self.title)
        self.root.addWidget(self.image)
        self.root.addWidget(self.subtitle)
        self.root.addStretch()
        self.root.addWidget(self.ok_pressed)

    def configure(self, title: str, image_path, subtitle: str):
        self.title.setText(title)
        if str(image_path).lower().endswith(".gif"):
            self._movie = QMovie(str(image_path))
            if self._movie.isValid():
                self.image.setMovie(self._movie)
                self._movie.start()
            else:
                self.image.setText("[Animación no disponible]")
                self.image.setStyleSheet("font-size:28px; color:#64748b;")
        else:
            pix = QPixmap(str(image_path)).scaled(360, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if pix.isNull():
                self.image.setText("[Imagen no disponible]")
                self.image.setStyleSheet("font-size:28px; color:#64748b;")
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
        self.message.setStyleSheet("font-size:52px; font-weight:800; color:#075985;")
        self.animation.setAlignment(Qt.AlignCenter)
        self.animation.setFixedHeight(230)

        self.root.addStretch()
        self.root.addWidget(self.message)
        self.root.addWidget(self.animation)
        self.root.addStretch()

    def set_message(self, text: str, gif_path=None):
        self.message.setText(text)
        self.animation.clear()
        if gif_path:
            self._movie = QMovie(str(gif_path))
            if self._movie.isValid():
                self.animation.setMovie(self._movie)
                self._movie.start()
            else:
                self.animation.setText("[Animación no disponible]")
                self.animation.setStyleSheet("font-size:24px; color:#64748b;")
