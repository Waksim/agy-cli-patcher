#!/usr/bin/env python3
"""Создаёт пропатченную копию Antigravity CLI 1.5.3 для Apple Silicon."""

import argparse
import hashlib
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


ORIGINAL_SHA256 = "5e4b545bff4a83a93354fc50c54631cf3e8cd02e1a469087af00929f3fdc4d51"
GOOGLE_SIGNATURE = 'identifier "cli" and anchor apple generic and certificate leaf[subject.OU] = "EQHXZ8M8AV"'

# Поле № 5 со списком сообщений IneligibleTier и именами в protobuf и JSON.
TIER_DESCRIPTOR = (
    b"\x12\x60\x0a\x10ineligible_tiers\x18\x05\x20\x03\x28\x0b"
    b"\x32\x35.google.internal.cloud.code.v1internal.IneligibleTier"
    b"\x52\x0fineligibleTiers"
)
PATCHED_DESCRIPTOR = TIER_DESCRIPTOR.replace(b"ineligible", b"inexigible")


class RussianArgumentParser(argparse.ArgumentParser):
    def format_usage(self) -> str:
        return f"Использование: python3 {self.prog} ИСХОДНИК КОПИЯ\n"

    def format_help(self) -> str:
        return (
            f"{self.description}\n\n{self.format_usage()}\n"
            "  ИСХОДНИК   Оригинальный agy с подписью Google\n"
            "  КОПИЯ      Путь к новому исполняемому файлу\n"
            "  -h, --help Показать справку\n"
        )

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, "Неверные аргументы. Справка доступна через --help.\n")


def codesign(error_message: str, *arguments: str) -> None:
    result = subprocess.run(["/usr/bin/codesign", *arguments], capture_output=True)
    if result.returncode:
        raise ValueError(f"{error_message} (код codesign {result.returncode})")


def build_copy(source: Path, output: Path) -> None:
    if sys.platform != "darwin" or platform.machine() != "arm64":
        raise ValueError("Запустите скрипт через нативный Python на Mac с Apple Silicon")
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Выходной файл уже существует: {output}")

    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("Требуется оригинальный agy 1.5.3 для Apple Silicon с подписью Google")
    codesign(
        "Не удалось проверить подпись Google у исходного файла",
        "--verify", "--strict", f"-R={GOOGLE_SIGNATURE}", str(source),
    )
    if original.count(TIER_DESCRIPTOR) != 1:
        raise ValueError("Требуется ровно одно совпадение дескриптора ineligible_tiers")

    patched = original.replace(TIER_DESCRIPTOR, PATCHED_DESCRIPTOR, 1)
    with tempfile.TemporaryDirectory(prefix=".agy-patch-", dir=output.parent) as directory:
        staged = Path(directory) / "agy"
        staged.write_bytes(patched)
        staged.chmod(0o755)
        codesign(
            "Не удалось подписать новую копию",
            "--force", "--sign", "-", "--preserve-metadata=identifier", str(staged),
        )
        codesign(
            "Не удалось проверить подпись новой копии", "--verify", "--strict", str(staged),
        )
        os.link(staged, output)


def main() -> None:
    parser = RussianArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        build_copy(args.source, args.output)
    except FileExistsError:
        parser.exit(1, f"Выходной файл уже существует: {args.output}\n")
    except OSError as error:
        parser.exit(1, f"Системная ошибка {error.errno}: {error.filename or args.output}\n")
    except ValueError as error:
        parser.exit(1, f"Ошибка: {error}\n")
    print(f"Создан файл {args.output}")


if __name__ == "__main__":
    main()
