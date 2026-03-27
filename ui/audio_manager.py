"""Queued audio playback helper with MP3 support and graceful fallback."""
from __future__ import annotations

import logging
from collections import deque
from pathlib import Path

from PyQt5.QtCore import QObject, QTimer, QUrl

logger = logging.getLogger(__name__)

try:
    from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
except ImportError:  # pragma: no cover - environment-dependent
    QMediaContent = None
    QMediaPlayer = None


class AudioManager(QObject):
    def __init__(self, audio_files: dict[str, object], parent: QObject | None = None):
        super().__init__(parent)
        self._audio_files = {name: str(path) for name, path in audio_files.items()}
        self._queue: deque[tuple[str, int]] = deque()
        self._missing_logged: set[str] = set()
        self._gap_timer = QTimer(self)
        self._gap_timer.setSingleShot(True)
        self._gap_timer.timeout.connect(self._play_next)
        self._next_gap_ms = 250

        self._available = QMediaPlayer is not None and QMediaContent is not None
        self._player = QMediaPlayer(self) if self._available else None
        if self._player is not None:
            self._player.setVolume(95)
            self._player.mediaStatusChanged.connect(self._handle_media_status)
            self._player.error.connect(self._handle_error)

    def play(self, name: str, gap_ms: int = 250, interrupt: bool = False):
        self.queue([name], gap_ms=gap_ms, interrupt=interrupt)

    def queue(self, names: list[str], gap_ms: int = 250, interrupt: bool = False):
        if not self._available:
            return
        if interrupt:
            self.stop()
        for name in names:
            self._queue.append((name, gap_ms))
        if not self._is_busy():
            self._play_next()

    def stop(self):
        self._queue.clear()
        self._gap_timer.stop()
        if self._player is not None:
            self._player.stop()

    def _is_busy(self) -> bool:
        if self._gap_timer.isActive():
            return True
        if self._player is None:
            return False
        return self._player.state() != QMediaPlayer.StoppedState

    def _handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self._gap_timer.start(self._next_gap_ms)
        elif status == QMediaPlayer.InvalidMedia:
            logger.warning("Invalid audio media")
            self._gap_timer.start(0)

    def _handle_error(self, error):
        if error == QMediaPlayer.NoError:
            return
        logger.warning("Audio playback error: %s", self._player.errorString() if self._player else error)

    def _play_next(self):
        if self._player is None or self._player.state() != QMediaPlayer.StoppedState or not self._queue:
            return

        name, gap_ms = self._queue.popleft()
        path = self._audio_files.get(name)
        self._next_gap_ms = gap_ms
        if not path:
            logger.warning("Audio key not configured: %s", name)
            self._gap_timer.start(0)
            return

        file_path = Path(path)
        if not file_path.exists():
            if name not in self._missing_logged:
                logger.warning("Audio file missing: %s", path)
                self._missing_logged.add(name)
            self._gap_timer.start(0)
            return

        self._player.setMedia(QMediaContent(QUrl.fromLocalFile(str(file_path))))
        self._player.play()
