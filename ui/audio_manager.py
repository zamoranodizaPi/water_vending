"""Queued audio playback helper with multiple backends and graceful fallback."""
from __future__ import annotations

import logging
import os
import shutil
from collections import deque
from pathlib import Path

from PyQt5.QtCore import QObject, QProcess, QTimer, QUrl

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

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.finished.connect(self._handle_process_finished)
        self._process.errorOccurred.connect(self._handle_process_error)
        self._process.readyReadStandardOutput.connect(self._handle_process_output)
        self._external_player = self._detect_external_player()

        self._qt_available = QMediaPlayer is not None and QMediaContent is not None
        self._player = QMediaPlayer(self) if self._qt_available else None
        if self._player is not None:
            self._player.setVolume(95)
            self._player.mediaStatusChanged.connect(self._handle_media_status)
            self._player.error.connect(self._handle_qt_error)

        if self._external_player:
            logger.info("Audio backend: external player %s", self._external_player[0])
        elif self._qt_available:
            logger.info("Audio backend: Qt multimedia")
        else:
            logger.warning("Audio backend unavailable")

    def play(self, name: str, gap_ms: int = 250, interrupt: bool = False):
        self.queue([name], gap_ms=gap_ms, interrupt=interrupt)

    def queue(self, names: list[str], gap_ms: int = 250, interrupt: bool = False):
        if interrupt:
            self.stop()
        for name in names:
            self._queue.append((name, gap_ms))
        if not self._is_busy():
            self._play_next()

    def stop(self):
        self._queue.clear()
        self._gap_timer.stop()
        if self._process.state() != QProcess.NotRunning:
            self._process.kill()
            self._process.waitForFinished(200)
        if self._player is not None:
            self._player.stop()

    def _detect_external_player(self) -> tuple[str, list[str]] | None:
        forced_player = os.getenv("VENDING_AUDIO_PLAYER", "").strip()
        if forced_player:
            forced_path = shutil.which(forced_player) or forced_player
            if Path(forced_path).exists():
                return forced_path, []

        candidates = (
            ("mpg123", ["-q"], ("/usr/bin/mpg123", "/usr/local/bin/mpg123")),
            ("mpg321", ["-q"], ("/usr/bin/mpg321", "/usr/local/bin/mpg321")),
            ("cvlc", ["--play-and-exit", "--quiet"], ("/usr/bin/cvlc", "/usr/local/bin/cvlc")),
            ("vlc", ["--intf", "dummy", "--play-and-exit", "--quiet"], ("/usr/bin/vlc", "/usr/local/bin/vlc")),
            ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet"], ("/usr/bin/ffplay", "/usr/local/bin/ffplay")),
            ("paplay", [], ("/usr/bin/paplay", "/usr/local/bin/paplay")),
            ("aplay", [], ("/usr/bin/aplay", "/usr/local/bin/aplay")),
        )
        for command, base_args, absolute_candidates in candidates:
            resolved = shutil.which(command)
            if resolved:
                return resolved, base_args
            for absolute_path in absolute_candidates:
                if Path(absolute_path).exists():
                    return absolute_path, base_args
        return None

    def _is_busy(self) -> bool:
        if self._gap_timer.isActive():
            return True
        if self._process.state() != QProcess.NotRunning:
            return True
        if self._player is not None and self._player.state() != QMediaPlayer.StoppedState:
            return True
        return False

    def _handle_process_finished(self, _exit_code: int, _exit_status):
        self._gap_timer.start(self._next_gap_ms)

    def _handle_process_error(self, error):
        if error == QProcess.UnknownError:
            return
        logger.warning("External audio playback error: %s", error)
        self._gap_timer.start(0)

    def _handle_process_output(self):
        output = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="ignore").strip()
        if output:
            logger.info("Audio player output: %s", output)

    def _handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self._gap_timer.start(self._next_gap_ms)
        elif status == QMediaPlayer.InvalidMedia:
            logger.warning("Invalid audio media")
            self._gap_timer.start(0)

    def _handle_qt_error(self, error):
        if error == QMediaPlayer.NoError:
            return
        logger.warning("Qt audio playback error: %s", self._player.errorString() if self._player else error)

    def _play_next(self):
        if self._is_busy() or not self._queue:
            return

        name, gap_ms = self._queue.popleft()
        path = self._audio_files.get(name)
        self._next_gap_ms = gap_ms
        if not path:
            logger.warning("Audio key not configured: %s", name)
            self._gap_timer.start(0)
            return

        file_path = Path(path)
        logger.info("Audio requested: key=%s path=%s", name, file_path)
        if not file_path.exists():
            if name not in self._missing_logged:
                logger.warning("Audio file missing: %s", path)
                self._missing_logged.add(name)
            self._gap_timer.start(0)
            return

        if self._play_with_external_player(file_path):
            return
        if self._play_with_qt(file_path):
            return

        logger.warning("No audio backend could play: %s", path)
        self._gap_timer.start(0)

    def _play_with_external_player(self, file_path: Path) -> bool:
        if not self._external_player:
            return False
        command, base_args = self._external_player
        args = [*base_args, str(file_path)]
        logger.info("Playing audio with external backend: %s %s", command, " ".join(args))
        self._process.start(command, args)
        if not self._process.waitForStarted(500):
            logger.warning("Failed to start external audio player: %s", command)
            return False
        return True

    def _play_with_qt(self, file_path: Path) -> bool:
        if self._player is None:
            return False
        logger.info("Playing audio with Qt backend: %s", file_path)
        self._player.setMedia(QMediaContent(QUrl.fromLocalFile(str(file_path))))
        self._player.play()
        return True
