"""Progress screen used for rinse and filling operations."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QSizePolicy, QVBoxLayout, QWidget

from config import settings
from theme import APP_FONT, SECONDARY, SURFACE, refresh_style

HEADER_HEIGHT = 90


class DispensingScreen(QWidget):
    progress_changed = pyqtSignal(int)
    completed = pyqtSignal()
    emergency_pressed = pyqtSignal()

    def __init__(self, logo_path):
        super().__init__()
        self.setObjectName("dispensingScreen")
        self.logo_path = logo_path
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._elapsed_ms = 0
        self._total_ms = 1
        self._movie = None
        self._image_pixmap = None
        self._image_offset_y = 0
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self.header_container = QFrame()
        self.header_container.setObjectName("modernHeader")
        self.header_container.setFixedHeight(HEADER_HEIGHT)
        header = QHBoxLayout(self.header_container)
        header.setContentsMargins(16, 10, 16, 10)
        header.setSpacing(0)

        header_icon = QLabel()
        header_icon.setAlignment(Qt.AlignCenter)
        header_icon.setFixedSize(72, 72)
        pix = QPixmap(str(self.logo_path))
        if pix.isNull():
            header_icon.setText("L")
            header_icon.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:{SURFACE};")
        else:
            header_icon.setPixmap(pix.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(header_icon, 0, Qt.AlignVCenter)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        text_col.addStretch(1)
        title = QLabel(settings.BRAND_TITLE)
        title.setStyleSheet(f"font-family:{APP_FONT}; font-size:25px; font-weight:800; color:{SURFACE};")
        text_col.addWidget(title)
        subtitle = QLabel(settings.BRAND_TAGLINE)
        subtitle.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:12px; font-weight:600; color:{SURFACE};"
        )
        text_col.addWidget(subtitle)
        text_col.addStretch(1)
        header.addLayout(text_col, 1)
        root.addWidget(self.header_container)

        content = QFrame()
        content.setObjectName("contentPanel")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(0)

        self.title = QLabel("Proceso")
        self.title.setObjectName("screenTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.status_hint = QLabel("Mantenga el recipiente en posición y espere a que termine.")
        self.status_hint.setAlignment(Qt.AlignCenter)
        self.status_hint.setWordWrap(True)
        self.status_hint.setStyleSheet(
            f"font-family:{APP_FONT}; font-size:16px; font-weight:600; color:{SECONDARY};"
        )

        self.animation_wrap = QWidget()
        self.animation_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.animation_wrap_layout = QVBoxLayout(self.animation_wrap)
        self.animation_wrap_layout.setContentsMargins(0, 0, 0, 0)
        self.animation_wrap_layout.setSpacing(0)

        self.animation = QLabel()
        self.animation.setObjectName("heroImage")
        self.animation.setAlignment(Qt.AlignCenter)
        self.animation.setFixedSize(360, 320)
        self.animation.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.animation_wrap_layout.addWidget(self.animation, 0, Qt.AlignHCenter)

        self.progress = QProgressBar()
        self.progress.setObjectName("processProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(52)
        self.progress.setFixedWidth(460)
        self.progress.setStyleSheet(f"QProgressBar{{font-family:{APP_FONT};}}")

        content_layout.addWidget(self.title)
        content_layout.addSpacing(8)
        content_layout.addWidget(self.status_hint)
        content_layout.addSpacing(8)
        content_layout.addStretch(1)
        content_layout.addWidget(self.animation_wrap, 0, Qt.AlignCenter)
        content_layout.addStretch(1)
        content_layout.addSpacing(30)
        content_layout.addWidget(self.progress, alignment=Qt.AlignCenter)
        root.addWidget(content, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_animation()

    def _refresh_animation(self):
        if self._movie and self._movie.isValid():
            self._movie.setScaledSize(self.animation.size())
            return
        if self._image_pixmap is None:
            return
        target = self.animation.size()
        if target.width() <= 0 or target.height() <= 0:
            return
        self.animation.setPixmap(self._image_pixmap.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _set_animation_slot(self, image_size=None, offset_y: int = 0):
        width, height = image_size or (360, 320)
        self.animation.setFixedSize(width, height)
        self._image_offset_y = offset_y
        top_margin = max(0, offset_y)
        bottom_margin = max(0, -offset_y)
        self.animation_wrap_layout.setContentsMargins(0, top_margin, 0, bottom_margin)
        self.animation_wrap.setFixedSize(width, height + top_margin + bottom_margin)
        self._refresh_animation()

    def set_credit(self, credit: float):
        return

    def start(
        self,
        title: str,
        total_seconds: float,
        gif_path=None,
        image_path=None,
        image_size=None,
        emergency_enabled: bool = False,
        image_offset_y: int = 0,
    ):
        self.title.setText(title)
        self._set_animation_slot(image_size=image_size, offset_y=image_offset_y)
        self._total_ms = max(500, int(total_seconds * 1000))
        self._elapsed_ms = 0
        self.progress.setValue(0)
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

        self._timer.start(200)

    def stop_now(self):
        self._timer.stop()

    def _tick(self):
        self._elapsed_ms += 200
        pct = min(100, int((self._elapsed_ms / self._total_ms) * 100))
        self.progress.setValue(pct)
        self.progress_changed.emit(pct)
        if pct >= 100:
            self._timer.stop()
            self.completed.emit()
