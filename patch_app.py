#!/usr/bin/env python3
"""Создаёт пропатченную копию Language Server Antigravity App 2.35.0 для Apple Silicon."""

from pathlib import Path

from patch_agy import RussianArgumentParser, build_copy


ORIGINAL_SHA256 = "7235d144514112b8dc86b38253590c69de306c32ba98408bd061bf36d532848b"
GOOGLE_SIGNATURE = (
    'identifier "language_server" and anchor apple generic '
    'and certificate leaf[subject.OU] = "EQHXZ8M8AV"'
)


def main() -> None:
    parser = RussianArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        build_copy(
            args.source,
            args.output,
            original_sha256=ORIGINAL_SHA256,
            google_signature=GOOGLE_SIGNATURE,
            source_description="Language Server Antigravity App 2.35.0",
        )
    except FileExistsError:
        parser.exit(1, f"Выходной файл уже существует: {args.output}\n")
    except OSError as error:
        parser.exit(1, f"Системная ошибка {error.errno}: {error.filename or args.output}\n")
    except ValueError as error:
        parser.exit(1, f"Ошибка: {error}\n")
    print(f"Создан файл {args.output}")


if __name__ == "__main__":
    main()
