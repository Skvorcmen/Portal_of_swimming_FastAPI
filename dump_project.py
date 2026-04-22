import os

# Файлы и папки которые НЕ нужны
EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".next",
    "dist",
    "build",
    "migrations",
    "tests",
    ".idea",
    "uploads",
}

EXCLUDE_FILES = {
    ".env",
    ".env.local",
    "cookies.txt",
    "app.log",
    "swimming_portal.db",
    "pytest.ini",
    "start.sh",
    "dump_project.py",
    "test_db.py",
    "test_jwt.py",
    "test_repo.py",
    "test_service.py",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".db",
    ".sqlite",
    ".log",
    ".pdf",
    ".csv",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".backup",
    ".backup2",
}

# Какие файлы включить (расширения)
INCLUDE_EXTENSIONS = {
    ".py",
    ".html",
    ".css",
    ".js",
    ".md",
    ".json",
    ".toml",
    ".ini",
    ".txt",
    ".yml",
    ".yaml",
}

# Максимальный размер файла (байт) чтобы не перегружать
MAX_FILE_SIZE = 50_000  # 50KB

OUTPUT_FILE = "project_context.md"


def should_include(filepath: str) -> bool:
    """Проверяем нужно ли включать файл"""
    parts = filepath.replace("\\", "/").split("/")

    # Проверяем папки
    for part in parts:
        if part in EXCLUDE_DIRS:
            return False

    filename = os.path.basename(filepath)

    # Проверяем исключённые файлы
    if filename in EXCLUDE_FILES:
        return False

    # Проверяем расширение
    _, ext = os.path.splitext(filename)
    if ext in EXCLUDE_EXTENSIONS:
        return False

    if ext not in INCLUDE_EXTENSIONS:
        return False

    return True


def get_language(filepath: str) -> str:
    """Определяем язык для подсветки синтаксиса"""
    ext_map = {
        ".py": "python",
        ".html": "html",
        ".css": "css",
        ".js": "javascript",
        ".md": "markdown",
        ".json": "json",
        ".toml": "toml",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".ini": "ini",
        ".txt": "text",
    }
    _, ext = os.path.splitext(filepath)
    return ext_map.get(ext, "text")


def collect_files(root_dir: str) -> list:
    """Собираем все файлы"""
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Убираем исключённые папки из обхода
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in sorted(filenames):
            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)

            if should_include(rel_path):
                size = os.path.getsize(filepath)
                files.append((rel_path, filepath, size))

    return sorted(files, key=lambda x: x[0])


def build_tree(files: list, root_dir: str) -> str:
    """Строим дерево файлов"""
    tree_lines = [f"{os.path.basename(root_dir)}/"]
    paths = [f[0] for f in files]

    dirs_seen = set()
    for path in paths:
        parts = path.replace("\\", "/").split("/")
        for i, part in enumerate(parts[:-1]):
            dir_path = "/".join(parts[: i + 1])
            if dir_path not in dirs_seen:
                indent = "  " * i
                tree_lines.append(f"{indent}├── {part}/")
                dirs_seen.add(dir_path)
        indent = "  " * (len(parts) - 1)
        tree_lines.append(f"{indent}├── {parts[-1]}")

    return "\n".join(tree_lines)


def dump_project(root_dir: str = "."):
    """Главная функция"""
    print(f"🔍 Сканирую проект...")

    files = collect_files(root_dir)

    print(f"📁 Найдено файлов: {len(files)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        # Заголовок
        out.write("# PROJECT CONTEXT DUMP\n\n")
        out.write(
            "> Этот файл содержит полный контекст проекта.\n"
            "> Изучи структуру и все файлы перед выполнением задачи.\n\n"
        )

        # Структура проекта
        out.write("---\n\n")
        out.write("## 📁 СТРУКТУРА ПРОЕКТА\n\n")
        out.write("```\n")
        out.write(build_tree(files, root_dir))
        out.write("\n```\n\n")

        # Содержимое файлов
        out.write("---\n\n")
        out.write("## 📄 СОДЕРЖИМОЕ ФАЙЛОВ\n\n")

        skipped = []

        for rel_path, filepath, size in files:
            rel_path_display = rel_path.replace("\\", "/")

            if size > MAX_FILE_SIZE:
                skipped.append(
                    f"{rel_path_display} " f"(слишком большой: {size // 1024}KB)"
                )
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
            except Exception as e:
                skipped.append(f"{rel_path_display} (ошибка чтения: {e})")
                continue

            if not content:
                continue

            lang = get_language(filepath)

            out.write(f"### `{rel_path_display}`\n\n")
            out.write(f"```{lang}\n")
            out.write(content)
            out.write("\n```\n\n")
            out.write("---\n\n")

            print(f"  ✅ {rel_path_display}")

        # Пропущенные файлы
        if skipped:
            out.write("## ⚠️ ПРОПУЩЕННЫЕ ФАЙЛЫ\n\n")
            for s in skipped:
                out.write(f"- {s}\n")
            out.write("\n")

        # В конце место для задачи
        out.write("---\n\n")
        out.write("## 🎯 ЗАДАЧА\n\n")
        out.write("> Впиши сюда задачу перед отправкой ИИ\n\n")
        out.write("```\n[ОПИСАНИЕ ЗАДАЧИ]\n```\n")

    # Итог
    output_size = os.path.getsize(OUTPUT_FILE)
    print(f"\n✅ Готово!")
    print(f"📄 Файл: {OUTPUT_FILE}")
    print(f"📦 Размер: {output_size // 1024}KB")
    print(f"⚠️  Пропущено: {len(skipped)} файлов")

    if output_size > 500_000:
        print(
            f"\n⚠️  ВНИМАНИЕ: файл больше 500KB.\n"
            f"   Возможно слишком большой для вставки в чат.\n"
            f"   Используй Claude.ai или ChatGPT с загрузкой файлов."
        )


if __name__ == "__main__":
    dump_project(".")
