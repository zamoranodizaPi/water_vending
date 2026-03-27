#!/usr/bin/env python3
"""Prueba standalone de reproduccion de audios del vending."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

from config import settings


def detect_player() -> tuple[str, list[str]] | None:
    candidates = (
        ("mpg123", ["-q"]),
        ("mpg321", ["-q"]),
        ("cvlc", ["--play-and-exit", "--quiet"]),
        ("vlc", ["--intf", "dummy", "--play-and-exit", "--quiet"]),
        ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet"]),
        ("paplay", []),
        ("aplay", []),
    )
    for command, base_args in candidates:
        if shutil.which(command):
            return command, base_args
    return None


def build_audio_map() -> dict[str, Path]:
    return {name: Path(path) for name, path in settings.AUDIO_FILES.items()}


def play_file(path: Path, player: tuple[str, list[str]]) -> int:
    command, base_args = player
    args = [command, *base_args, str(path)]
    print(f"Reproduciendo: {path.name}")
    print("Comando:", " ".join(args))
    completed = subprocess.run(args, check=False)
    return completed.returncode


def resolve_targets(args: argparse.Namespace, audio_map: dict[str, Path]) -> list[tuple[str, Path]]:
    if args.all:
        return list(audio_map.items())

    if args.key:
        path = audio_map.get(args.key)
        if path is None:
            raise SystemExit(f"Audio no encontrado para key: {args.key}")
        return [(args.key, path)]

    if args.file:
        path = Path(args.file).expanduser().resolve()
        return [(path.stem, path)]

    raise SystemExit("Debes usar --all, --key <nombre> o --file <ruta>")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prueba standalone de audios del vending")
    parser.add_argument("--list", action="store_true", help="Lista los audios configurados")
    parser.add_argument("--all", action="store_true", help="Reproduce todos los audios configurados")
    parser.add_argument("--key", help="Reproduce un audio por key de config/settings.py")
    parser.add_argument("--file", help="Reproduce un archivo de audio especifico")
    parser.add_argument("--gap", type=float, default=0.6, help="Pausa entre audios en segundos")
    parsed = parser.parse_args()

    audio_map = build_audio_map()

    if parsed.list:
        print("Audios configurados:")
        for name, path in sorted(audio_map.items()):
            status = "OK" if path.exists() else "FALTA"
            print(f"- {name:24} {status}  {path}")
        return 0

    player = detect_player()
    if player is None:
        print("No se encontro reproductor externo.")
        print("Instala uno de estos en la Raspberry: mpg123, mpg321, vlc o ffplay.")
        return 1

    print(f"Backend detectado: {player[0]}")
    targets = resolve_targets(parsed, audio_map)

    failures = 0
    for key, path in targets:
        print(f"\n[{key}]")
        if not path.exists():
            print(f"Archivo no encontrado: {path}")
            failures += 1
            continue
        code = play_file(path, player)
        if code != 0:
            print(f"Fallo al reproducir {path.name}. Exit code: {code}")
            failures += 1
        time.sleep(max(0.0, parsed.gap))

    if failures:
        print(f"\nTerminado con errores: {failures}")
        return 1

    print("\nPrueba completada sin errores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
