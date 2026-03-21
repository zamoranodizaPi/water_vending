"""Small WAV playback helper with graceful fallback when audio is unavailable."""
from __future__ import annotations

import logging
from collections import deque

from PyQt5.QtCore import QObject, QTimer, QUrl

logger = logging.getLogger(__name__)

try:
    from PyQt5.QtMultimedia import QSoundEffect
except ImportError:  # pragma: no cover - environment-dependent
    QSoundEffect = None


class AudioManager(QObject):
    def __init__(self, audio_files: dict[str, object], parent: QObject | None = None):
        super().__init__(parent)
        self._audio_files = {name: str(path) for name, path in audio_files.items()}
        self._queue: deque[tuple[str, int]] = deque()
        self._missing_logged: set[str] = set()
        self._available = QSoundEffect is not None

        self._effect = QSoundEffect(self) if self._available else None
        if self._effect is not None:
            self._effect.setVolume(0.95)
            self._effect.playingChanged.connect(self._handle_playback_change)

    def play(self, name: str):
        self.queue([name])

    def queue(self, names: list[str], gap_ms: int = 250):
        if not self._available:
            return
        for name in names:
            self._queue.append((name, gap_ms))
        if not self._effect.isPlaying():
            self._play_next()

    def _handle_playback_change(self):
        if self._effect is None or self._effect.isPlaying():
            return
        if self._queue:
            _, gap_ms = self._queue[0]
            QTimer.singleShot(gap_ms, self._play_next)

    def _play_next(self):
        if self._effect is None or self._effect.isPlaying() or not self._queue:
            return

        name, _gap_ms = self._queue.popleft()
        path = self._audio_files.get(name)
        if not path:
            logger.warning("Audio key not configured: %s", name)
            QTimer.singleShot(0, self._play_next)
            return
        if not QUrl.fromLocalFile(path).isLocalFile():
            QTimer.singleShot(0, self._play_next)
            return

        from pathlib import Path

        if not Path(path).exists():
            if name not in self._missing_logged:
                logger.warning("Audio file missing: %s", path)
                self._missing_logged.add(name)
            QTimer.singleShot(0, self._play_next)
            return

        self._effect.setSource(QUrl.fromLocalFile(path))
        self._effect.play()
