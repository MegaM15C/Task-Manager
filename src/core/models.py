from __future__ import annotations

"""Основные модели данных приложения (настройки, категории, задачи)."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal, Optional

ThemeName = Literal["light", "dark"]


class ViewKey:
    """Константы ключей видов для навигации (сайдбар → главное окно)."""

    ALL = "all"
    DEADLINES = "deadlines"
    IMPORTANT = "important"
    DONE = "done"
    CATEGORY_PREFIX = "category:"

    @staticmethod
    def category(cat_id: str) -> str:
        return f"category:{cat_id}"


@dataclass(frozen=True)
class Settings:
    """Настройки внешнего вида приложения.

    Атрибуты:
        accent_color: Цвет акцентов (кнопки, выделения).
        theme: Имя темы — светлая или тёмная.
        font_family: Основное семейство шрифтов для интерфейса.
    """

    accent_color: str = "#6D5EF6"
    theme: ThemeName = "light"
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
        priority: Приоритет задачи. Чем больше — тем важнее (сортируется выше).
        important: Флаг «важная» задача.
        done: Флаг выполнения.
        done_at: Дата-время, когда задача была отмечена выполненной (для сортировки в «Выполненные»).
    """

    id: str
    title: str
    category_id: Optional[str]
    due: Optional[date]
    priority: int = 0
    important: bool = False
    done: bool = False
    done_at: Optional[datetime] = None
