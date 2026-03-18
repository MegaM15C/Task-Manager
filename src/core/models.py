from __future__ import annotations

"""Основные модели данных приложения (настройки, категории, задачи)."""

from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional


ThemeName = Literal["light", "dark"]


@dataclass(frozen=True)
class Settings:
    """Настройки внешнего вида приложения.

    Атрибуты:
        accent_color: Цвет акцентов (кнопки, выделения).
        theme: Имя темы — светлая или тёмная.
        font_family: Основное семейство шрифтов для интерфейса.
    """

    accent_color: str = "#6D5EF6"
    theme: ThemeName = "dark"
    font_family: str = "Ubuntu Sans"


@dataclass(frozen=True)
class Category:
    """Категория задач (например, «Работа», «Личное»)."""

    id: str
    name: str
    color: str
    icon_filename: Optional[str] = None  # путь к иконке внутри AppPaths.icons_dir


@dataclass(frozen=True)
class Task:
    """Отдельная задача в списке.

    Атрибуты:
        id: Уникальный идентификатор (UUID в hex).
        title: Заголовок/краткое описание задачи.
        category_id: ID категории, к которой относится задача, или None.
        due: Дата дедлайна или None, если не задана.
        important: Флаг «важная» задача.
        done: Флаг выполнения.
    """

    id: str
    title: str
    category_id: Optional[str]
    due: Optional[date]
    important: bool = False
    done: bool = False
