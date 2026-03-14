"""Progress screen used for rinse and filling operations."""
from __future__ import annotations

from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSizePolicy


class DispensingScreen(QWidget):
    progress_changed = pyqtSignal(int)
    completed = pyqtSignal()
    emergency_pressed = pyqtSignal()

    def __init__(self, logo_path):
        super().__init__()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._elapsed_ms = 0
        self._total_ms = 1
        self._movie = None
        self._build_ui(logo_path)

    def _build_ui(self, logo_path):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 6, 12, 6)

        header = QHBoxLayout()
        title1 = QLabel("Agua Purificada ")
        title1.setAlignment(Qt.AlignCenter)
        title1.setStyleSheet("font-size:42px; font-weight:800; color:#0e7490;")
        title2 = QLabel("Lupita")
        title2.setAlignment(Qt.AlignCenter)
        title2.setStyleSheet("font-size:46px; font-family:'Brush Script MT'; color:#ec4899;")
        logo = QLabel()
        logo.setFixedSize(192, 144)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(logo_path)).scaled(176, 132, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        title1.setStyleSheet("font-size:34px; font-weight:800; color:#0e7490;")
        title2 = QLabel("Lupita")
        title2.setAlignment(Qt.AlignCenter)
        title2.setStyleSheet("font-size:38px; font-family:'Brush Script MT'; color:#ec4899;")
        logo = QLabel()
        logo.setFixedSize(96, 72)
        logo.setAlignment(Qt.AlignCenter)
        pix = QPixmap(str(logo_path)).scaled(88, 66, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if pix.isNull():
            logo.setText("Lupita")
            logo.setStyleSheet("font-size:18px; color:#0e7490;")
        else:
            logo.setPixmap(pix)
        header.addStretch()
        header.addWidget(title1)
        header.addWidget(title2)
        header.addSpacing(14)
        header.addWidget(logo)
        header.addStretch()
        root.addLayout(header)

        self.title = QLabel("Proceso")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:40px; font-weight:800; color:#0f766e;")

        self.animation = QLabel()
        self.animation.setAlignment(Qt.AlignCenter)
        self.animation.setFixedHeight(130)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(56)
        self.progress.setFixedWidth(430)
        self.progress.setStyleSheet(
            "QProgressBar{font-size:24px; border:4px solid #2563eb; border-radius:16px; text-align:center; background:#dbeafe;}"
            "QProgressBar::chunk{background:#ec4899; border-radius:12px;}"
        )

        self.emergency_btn = QPushButton("Paro")
        self.emergency_btn.setMinimumHeight(53)
        self.emergency_btn.setMinimumWidth(227)
        self.emergency_btn.setMaximumWidth(340)
        self.emergency_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.emergency_btn.setStyleSheet("font-size:24px; font-weight:800; background:#ef4444; color:white; border-radius:12px;")
        self.emergency_btn.clicked.connect(self.emergency_pressed.emit)
        self.emergency_btn.setVisible(False)

        root.addStretch()
        root.addWidget(self.title)
        root.addWidget(self.animation)
        root.addWidget(self.progress, alignment=Qt.AlignCenter)
        root.addSpacing(12)
        root.addWidget(self.emergency_btn, alignment=Qt.AlignCenter)
        root.addStretch()

    def start(self, title: str, total_seconds: float, gif_path=None, emergency_enabled: bool = False):
        self.title.setText(title)
        self._total_ms = max(500, int(total_seconds * 1000))
        self._elapsed_ms = 0
        self.progress.setValue(0)
        self.emergency_btn.setVisible(emergency_enabled)
        self.animation.clear()

        if gif_path:
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
