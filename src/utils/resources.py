from __future__ import annotations

"""Разрешение путей к ресурсам приложения в dev-режиме и в PyInstaller-бандле."""

import sys
from pathlib import Path


def resource_path(relative: str | Path) -> Path:
    """Возвращает абсолютный путь к файлу ресурса.

    В PyInstaller-бандле файлы распаковываются в sys._MEIPASS.
    В dev-режиме за корень проекта принимается директория на три уровня выше
    этого файла (src/utils/resources.py → проект).
    """
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent.parent
    return base / relative
