from __future__ import annotations

"""Работа с путями к файлам конфигурации и данным приложения."""

from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_dir


@dataclass(frozen=True)
class AppPaths:
    """Инкапсулирует все директории и файлы данных приложения.

    Использует библиотеку platformdirs, чтобы автоматически подобрать
    корректную директорию конфигурации под текущую ОС (Linux, Windows, macOS).
    """

    app_name: str = "TaskManagerApp"

    @property
    def config_dir(self) -> Path:
        """Корневая конфигурационная директория приложения в профиле пользователя."""
        return Path(user_config_dir(self.app_name))

    @property
    def data_dir(self) -> Path:
        """Поддиректория с данными (JSON-файлы, страницы задач)."""
        return self.config_dir / "data"

    @property
    def icons_dir(self) -> Path:
        """Поддиректория, в которую копируются пользовательские иконки категорий."""
        return self.config_dir / "icons"

    @property
    def tasks_pages_dir(self) -> Path:
        """Поддиректория со страницами задач (page_0001.json и т.д.)."""
        return self.data_dir / "tasks_pages"

    @property
    def settings_file(self) -> Path:
        """Путь к JSON-файлу с настройками приложения."""
        return self.data_dir / "settings.json"

    @property
    def categories_file(self) -> Path:
        """Путь к JSON-файлу со списком категорий."""
        return self.data_dir / "categories.json"

    def ensure(self) -> None:
        """Создаёт все нужные директории, если они ещё не существуют."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_pages_dir.mkdir(parents=True, exist_ok=True)
