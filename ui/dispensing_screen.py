"""Progress screen used for rinse and filling operations."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSizePolicy, QFrame

APP_FONT = "'Spicy Rice','DejaVu Sans'"
HEADER_STYLE = "QWidget{background:#0d6efd; border-radius:20px;}"
SECTION_TITLE_STYLE = f"font-family:{APP_FONT}; font-size:32px; font-weight:900; color:#0d6efd;"
STOP_BUTTON_STYLE = (
    f"QPushButton{{font-family:{APP_FONT}; font-size:22px; font-weight:800; background:#dc3545; color:white; "
    "border-radius:16px; border:none; padding:8px 20px;}}"
    "QPushButton:hover{background:#bb2d3b;}"
)


class DispensingScreen(QWidget):
    progress_changed = pyqtSignal(int)
    completed = pyqtSignal()
    emergency_pressed = pyqtSignal()

    def __init__(self, logo_path):
        super().__init__()
        self.setStyleSheet("QWidget { background:#f3f7fb; }")
        self.logo_path = logo_path
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._elapsed_ms = 0
        self._total_ms = 1
        self._movie = None
        self._build_ui(logo_path)

    def _build_ui(self, logo_path):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(0)

        self.header_container = QFrame()
        self.header_container.setFixedHeight(82)
        self.header_container.setStyleSheet(HEADER_STYLE)
        header = QHBoxLayout(self.header_container)
        header.setContentsMargins(20, 10, 20, 10)
        header.setSpacing(12)

        self.logo = QLabel(self.header_container)
        self.logo.setFixedSize(920, 82)
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("background: transparent;")
        pix = QPixmap(str(logo_path)).scaled(900, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            self.logo.setText("Lupita")
            self.logo.setStyleSheet(f"font-family:{APP_FONT}; font-size:24px; font-weight:800; color:#ffffff;")
        else:
            self.logo.setPixmap(pix)
        header.addWidget(self.logo, 1, Qt.AlignCenter)
        root.addWidget(self.header_container)

        self.title = QLabel("Proceso")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(SECTION_TITLE_STYLE)

        self.animation = QLabel()
        self.animation.setAlignment(Qt.AlignCenter)
        self.animation.setMinimumHeight(180)
        self.animation.setMaximumHeight(210)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(56)
        self.progress.setFixedWidth(430)
        self.progress.setStyleSheet(
            f"QProgressBar{{font-family:{APP_FONT}; font-size:22px; font-weight:700; border:3px solid #0d6efd; "
            "border-radius:16px; text-align:center; background:#ffffff; color:#1f2937;}"
            "QProgressBar::chunk{background:#0d6efd; border-radius:12px;}"
        )

        self.emergency_btn = QPushButton("Detener")
        self.emergency_btn.setMinimumHeight(56)
        self.emergency_btn.setMinimumWidth(240)
        self.emergency_btn.setMaximumWidth(320)
        self.emergency_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.emergency_btn.setStyleSheet(STOP_BUTTON_STYLE)
        self.emergency_btn.clicked.connect(self.emergency_pressed.emit)
        self.emergency_btn.setVisible(False)

        root.addSpacing(10)
        root.addWidget(self.title)
        root.addSpacing(8)
        root.addWidget(self.animation)
        root.addSpacing(16)
        root.addWidget(self.progress, alignment=Qt.AlignCenter)
        root.addSpacing(14)
        root.addWidget(self.emergency_btn, alignment=Qt.AlignCenter)
        root.addStretch()

    def set_credit(self, credit: float):
        return

    def start(self, title: str, total_seconds: float, gif_path=None, image_path=None, image_size=None, emergency_enabled: bool = False):
        self.title.setText(title)
        self._total_ms = max(500, int(total_seconds * 1000))
        self._elapsed_ms = 0
        self.progress.setValue(0)
        self.emergency_btn.setVisible(emergency_enabled)
        self.animation.clear()
        self.animation.setMovie(None)
        self._movie = None

        if image_path:
            width, height = image_size or (220, 180)
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
                self.animation.setMovie(self._movie)
                self._movie.start()
            else:
                self.animation.setText("[Animación no disponible]")
                self.animation.setStyleSheet("font-size:22px; color:#64748b;")

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
