#!/usr/bin/env python3
"""
Этот скрипт обходит все файлы и папки, начиная с указанной корневой директории,
и объединяет содержимое всех файлов в один выходной файл.
Перед началом каждого файла выводится строка:
#! begin `<относительный_путь_до_файла>`
после содержимого — строка:
#! end `<относительный_путь_до_файла>`

Список исключений задаётся внутри скрипта через глобальную переменную EXCLUDE_PATTERNS
(паттерны glob для файлов и директорий).
"""
import os
import argparse
import fnmatch

# Паттерны для исключения файлов и папок
EXCLUDE_PATTERNS = [
    "*.tmp",
    "*.log",
    "*.css",
    "*.js",
    ".venv/*",
    ".git/*",
    "*__pycache__*",
    ".idea/*",
    "uploads/*",
    "build/*",
    "vendor/*",
]

INCLUDE_PATTERNS = [
    "assets/css/main.css",
]


def matches_any(path: str, patterns: list) -> bool:
    """
    Проверяет, соответствует ли путь любому из паттернов.
    """
    return any(fnmatch.fnmatch(path, pat) for pat in patterns)


def should_exclude(path: str) -> bool:
    """
    Нужно ли исключить путь по EXCLUDE_PATTERNS.
    """
    return matches_any(path, EXCLUDE_PATTERNS)


def should_include(path: str) -> bool:
    """
    Нужно ли принудительно включить путь, даже если он в исключениях.
    """
    return matches_any(path, INCLUDE_PATTERNS)


def is_text_file(path: str) -> bool:
    """
    Проверяет, можно ли прочитать файл как текст UTF-8.
    Читает первые несколько байт и пытается декодировать.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, OSError):
        return False


def collect_and_write(root: str, output: str) -> None:
    """
    Обходит дерево директории root, пропуская по EXCLUDE_PATTERNS,
    и записывает в output:
      #! begin `<relative_path>`
      <содержимое файла>
      #! end `<relative_path>`
    """
    with open(output, "w", encoding="utf-8") as out_f:
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)

            # Фильтрация директорий по исключениям (override include)
            dirnames[:] = [d for d in dirnames
                           if not should_exclude(os.path.normpath(os.path.join(rel_dir, d)))
                           or should_include(os.path.normpath(os.path.join(rel_dir, d)))]

            for fname in filenames:
                rel_file = os.path.normpath(os.path.join(rel_dir, fname))
                full_path = os.path.join(dirpath, fname)

                # Пропустить по исключениям, если не в include
                if should_exclude(rel_file) and not should_include(rel_file):
                    continue
                # Пропустить, если не текстовый
                if not is_text_file(full_path):
                    continue

                # Начало файла
                out_f.write(f"### begin `{rel_file}` ###\n")
                try:
                    with open(full_path, "r", encoding="utf-8") as in_f:
                        out_f.write(in_f.read())
                except Exception as e:
                    print(f"Не удалось прочитать файл {full_path}: {e}")
                # Конец файла
                out_f.write(f"\n### end `{rel_file}` ###\n\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Объединяет файлы в один с метками начала и конца каждого файла."
    )
    parser.add_argument("root", help="Корневая директория для обхода")
    parser.add_argument("output", help="Путь к выходному файлу")
    return parser.parse_args()


def main():
    args = parse_args()
    collect_and_write(args.root, args.output)


if __name__ == "__main__":
    main()
