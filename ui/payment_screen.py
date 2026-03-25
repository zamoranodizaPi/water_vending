"""Instruction and message screens with consistent kiosk branding."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from theme import APP_FONT, SECONDARY, SURFACE, TEXT_PRIMARY, refresh_style

HEADER_HEIGHT = 90
TITLE_TEXT = "Agua Purificada Lupita"
TAGLINE_TEXT = "La pureza que nace de la confianza"


class BrandedScreen(QWidget):
    def __init__(self, logo_path):
        super().__init__()
        self.setObjectName("screen")
        self.logo_path = logo_path
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(12, 10, 12, 10)
        self.root.setSpacing(10)
        self._build_header()
        self.content = QFrame()
        self.content.setObjectName("contentPanel")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(20, 16, 20, 16)
        self.content_layout.setSpacing(0)
        self.root.addWidget(self.content, 1)

    def _build_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("modernHeader")
        self.header_frame.setFixedHeight(HEADER_HEIGHT)

        title_row = QHBoxLayout(self.header_frame)
        title_row.setContentsMargins(16, 10, 16, 10)
        title_row.setSpacing(0)

        self.header_icon = QLabel()
        self.header_icon.setAlignment(Qt.AlignCenter)
        self.header_icon.setFixedSize(94, 94)
        pix = QPixmap(str(self.logo_path))
        if pix.isNull():
            self.header_icon.setText("L")
            self.header_icon.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:{SURFACE};")
        else:
            self.header_icon.setPixmap(pix.scaled(94, 94, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_row.addWidget(self.header_icon, 0, Qt.AlignVCenter)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        text_col.addStretch(1)
        title = QLabel(TITLE_TEXT)
        title.setStyleSheet(f"font-family:{APP_FONT}; font-size:25px; font-weight:800; color:{SURFACE};")
        text_col.addWidget(title)
        subtitle = QLabel(TAGLINE_TEXT)
        subtitle.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:12px; font-weight:600; color:{SURFACE};"
        )
        text_col.addWidget(subtitle)
        text_col.addStretch(1)
        title_row.addLayout(text_col, 1)

        self.root.addWidget(self.header_frame)

    def set_credit(self, credit: float):
        return


class PromptScreen(BrandedScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.setObjectName("promptScreen")
        self.ok_pressed = QPushButton("OK")
        self._movie = None
        self._image_pixmap = None
        self._image_offset_y = 0
        self._footer_hint_base = "Presione OK cuando esté listo"
        self._build_ui()

    def _build_ui(self):
        self.title = QLabel("Instrucción")
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.image_wrap = QWidget()
        self.image_wrap_layout = QVBoxLayout(self.image_wrap)
        self.image_wrap_layout.setContentsMargins(0, 0, 0, 0)
        self.image_wrap_layout.setSpacing(0)

        self.image = QLabel()
        self.image.setObjectName("heroImage")
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setFixedSize(360, 320)
        self.image.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.image_wrap_layout.addWidget(self.image, 0, Qt.AlignHCenter)

        self.subtitle = QLabel("")
        self.subtitle.setObjectName("bodyText")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)

        self.footer_hint = QLabel(self._footer_hint_base)
        self.footer_hint.setAlignment(Qt.AlignCenter)
        self.footer_hint.setWordWrap(True)
        self.footer_hint.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:16px; font-weight:600; color:{SECONDARY};"
        )

        self.ok_pressed.setObjectName("confirmButton")
        self.ok_pressed.setMinimumHeight(48)
        self.ok_pressed.setMinimumWidth(190)
        self.ok_pressed.setVisible(False)

        self.content_layout.addWidget(self.title)
        self.content_layout.addSpacing(10)
        self.content_layout.addStretch(1)
        self.content_layout.addWidget(self.image_wrap, 0, Qt.AlignCenter)
        self.content_layout.addSpacing(16)
        self.content_layout.addWidget(self.subtitle)
        self.content_layout.addSpacing(10)
        self.content_layout.addWidget(self.footer_hint)
        self.content_layout.addSpacing(16)
        self.content_layout.addWidget(self.ok_pressed, 0, Qt.AlignCenter)
        self.content_layout.addStretch(1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_image()

    def _refresh_image(self):
        if self._movie and self._movie.isValid():
            self._movie.setScaledSize(self.image.size())
            return
        if self._image_pixmap is None:
            return
        target = self.image.size()
        if target.width() <= 0 or target.height() <= 0:
            return
        self.image.setPixmap(self._image_pixmap.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _set_image_slot(self, image_size=None, offset_y: int = 0):
        width, height = image_size or (360, 320)
        self.image.setFixedSize(width, height)
        self._image_offset_y = offset_y
        top_margin = max(0, offset_y)
        bottom_margin = max(0, -offset_y)
        self.image_wrap_layout.setContentsMargins(0, top_margin, 0, bottom_margin)
        self._refresh_image()

    def set_prompt_countdown(self, seconds: int | None):
        if seconds is None:
            self.footer_hint.setText(self._footer_hint_base)
            return
        self.footer_hint.setText(f"{self._footer_hint_base} ({seconds})")

    def configure(self, title: str, image_path, subtitle: str, image_size=None, image_offset_y: int = 0):
        self.title.setText(title)
        self._set_image_slot(image_size=image_size, offset_y=image_offset_y)
        self.image.setMovie(None)
        self._movie = None
        self._image_pixmap = None
        if str(image_path).lower().endswith(".gif"):
            self._movie = QMovie(str(image_path))
            if self._movie.isValid():
                self.image.setMovie(self._movie)
                self._movie.setScaledSize(self.image.size())
                self._movie.start()
            else:
                self.image.setText("[Animación no disponible]")
                self.image.setProperty("role", "secondary")
                self.image.setStyleSheet("font-size:22px;")
                refresh_style(self.image)
        else:
            pix = QPixmap(str(image_path))
            if pix.isNull():
                self.image.setText("[Imagen no disponible]")
                self.image.setProperty("role", "secondary")
                self.image.setStyleSheet("font-size:22px;")
                refresh_style(self.image)
            else:
                self._image_pixmap = pix
                self.image.setProperty("role", "")
                self.image.setStyleSheet("")
                refresh_style(self.image)
                self._refresh_image()
        self.subtitle.setText(subtitle)


class MessageScreen(BrandedScreen):
    def __init__(self, logo_path):
        super().__init__(logo_path)
        self.setObjectName("messageScreen")
        self._movie = None
        self._image_pixmap = None
        self._thank_you_mode = False
        self.message = QLabel("")
        self.animation = QLabel()
        self._build_ui()

    def _build_ui(self):
        self.message.setObjectName("screenTitle")
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setWordWrap(True)
        self.animation.setObjectName("heroImage")
        self.animation.setAlignment(Qt.AlignCenter)
        self.animation.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.animation.setMinimumSize(0, 0)
        self._apply_layout_mode()

    def _clear_content_layout(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(self.content)

    def _apply_layout_mode(self):
        self._clear_content_layout()
        self.header_frame.setVisible(not self._thank_you_mode)
        self.content.setProperty("thankyou", self._thank_you_mode)
        refresh_style(self.content)
        if self._thank_you_mode:
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            self.message.setVisible(False)
            self.content_layout.addWidget(self.animation, 1, Qt.AlignCenter)
            return
        self.content_layout.setContentsMargins(20, 16, 20, 16)
        self.message.setVisible(True)
        self.content_layout.addWidget(self.message)
        self.content_layout.addSpacing(18)
        self.content_layout.addWidget(self.animation, 1, Qt.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_animation()

    def _refresh_animation(self):
        target = self.animation.size()
        if self._movie and self._movie.isValid():
            self._movie.setScaledSize(target)
            return
        if self._image_pixmap is None:
            return
        if target.width() <= 0 or target.height() <= 0:
            return
        self.animation.setPixmap(self._image_pixmap.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def set_message(self, text: str, gif_path=None, image_path=None, image_size=None, hide_header: bool = False):
        self._thank_you_mode = hide_header
        if hide_header:
            self.animation.setFixedSize(472, 693)
        else:
            width, height = image_size or (360, 320)
            self.animation.setFixedSize(width, height)
        self._apply_layout_mode()
        self.message.setText(text)
        self.message.setObjectName("screenTitle")
        refresh_style(self.message)
        self.animation.clear()
        self.animation.setMovie(None)
        self._movie = None
        self._image_pixmap = None
        if image_path:
            pix = QPixmap(str(image_path))
            if pix.isNull():
                self.animation.setText("[Imagen no disponible]")
                self.animation.setProperty("role", "secondary")
                self.animation.setStyleSheet("font-size:22px;")
                refresh_style(self.animation)
            else:
                self._image_pixmap = pix
                self.animation.setProperty("role", "")
                self.animation.setStyleSheet("")
                refresh_style(self.animation)
                self._refresh_animation()
        elif gif_path:
            self._movie = QMovie(str(gif_path))
            if self._movie.isValid():
                self.animation.setMovie(self._movie)
                self._movie.setScaledSize(self.animation.size())
                self._movie.start()
            else:
                self.animation.setText("[Animación no disponible]")
                self.animation.setProperty("role", "secondary")
                self.animation.setStyleSheet("font-size:22px;")
                refresh_style(self.animation)
