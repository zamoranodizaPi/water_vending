#!/usr/bin/env python3
"""Reproductor standalone de un solo audio para uso desde la UI."""

from __future__ import annotations

import argparse
import os
import shutil
import shlex
import subprocess
import sys
from pathlib import Path

from config import settings


def detect_player() -> tuple[str, list[str]] | None:
    forced_player = os.getenv("VENDING_AUDIO_PLAYER", "").strip()
    forced_args = shlex.split(os.getenv("VENDING_AUDIO_ARGS", "").strip())
    if forced_player:
        forced_path = shutil.which(forced_player) or forced_player
        if Path(forced_path).exists():
            return forced_path, forced_args

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
            return resolved, forced_args or base_args
        for absolute_path in absolute_candidates:
            if Path(absolute_path).exists():
                return absolute_path, forced_args or base_args
    return None


def resolve_audio(key: str | None, file_path: str | None) -> Path:
    if file_path:
        return Path(file_path).expanduser().resolve()
    if not key:
        raise SystemExit("Debes indicar --key o --file")
    path = settings.AUDIO_FILES.get(key)
    if path is None:
        raise SystemExit(f"Audio no configurado: {key}")
    return Path(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproduce un audio del vending")
    parser.add_argument("--key", help="Key configurada en settings.AUDIO_FILES")
    parser.add_argument("--file", help="Ruta de archivo a reproducir")
    args = parser.parse_args()

    audio_path = resolve_audio(args.key, args.file)
    if not audio_path.exists():
        print(f"Archivo no encontrado: {audio_path}", file=sys.stderr)
        return 1

    player = detect_player()
    if player is None:
        print("No se encontro reproductor de audio", file=sys.stderr)
        return 1

    command, base_args = player
    completed = subprocess.run([command, *base_args, str(audio_path)], check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
