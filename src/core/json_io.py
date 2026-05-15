from __future__ import annotations

"""Утилиты чтения и записи JSON-файлов."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def read_json(path: Path, *, default: Any) -> Any:
    """Безопасно читает JSON-файл.

    Если файл не существует или повреждён, возвращает переданный default.
    Это позволяет не падать при первой загрузке или при некорректном файле.
    """
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        logger.warning("Повреждённый JSON в %s: %s", path, exc)
        return default


def write_json_atomic(path: Path, data: Any) -> None:
    """Записывает данные в JSON-файл атомарно.

    Сначала создаётся временный файл *.tmp, в который пишется JSON,
    затем он переименовывается в целевой путь. Так мы избегаем ситуаций,
    когда приложение внезапно завершается посреди записи и файл остаётся битым.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(path)
    except OSError as exc:
        logger.error("Ошибка записи в %s: %s", path, exc)
        raise
