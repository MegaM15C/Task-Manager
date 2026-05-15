from __future__ import annotations

"""Репозитории для работы с JSON-данными (настройки, категории, задачи)."""

import shutil
import uuid
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from .json_io import read_json, write_json_atomic
from .models import Category, Settings, Task
from .paths import AppPaths


def _today() -> date:
    """Возвращает сегодняшнюю дату (выделено в функцию для удобства тестирования)."""
    return date.today()


def _task_to_json(task: Task) -> dict:
    """Преобразует объект Task в словарь, готовый к сериализации в JSON."""
    d = asdict(task)
    d["due"] = task.due.isoformat() if task.due else None
    d["done_at"] = task.done_at.isoformat() if task.done_at else None
    return d


def _task_from_json(d: dict) -> Task:
    """Создаёт объект Task из словаря, прочитанного из JSON."""
    due = d.get("due")
    done_at = d.get("done_at")
    return Task(
        id=str(d["id"]),
        title=str(d.get("title", "")),
        category_id=d.get("category_id"),
        due=date.fromisoformat(due) if due else None,
        priority=int(d.get("priority", 0) or 0),
        important=bool(d.get("important", False)),
        done=bool(d.get("done", False)),
        done_at=datetime.fromisoformat(done_at) if done_at else None,
    )


def _category_to_json(cat: Category) -> dict:
    """Преобразует Category в словарь для записи в JSON."""
    return asdict(cat)


def _category_from_json(d: dict) -> Category:
    """Создаёт Category из словаря, прочитанного из JSON."""
    return Category(
        id=str(d["id"]),
        name=str(d.get("name", "")),
        color=str(d.get("color", "#888888")),
        icon_filename=d.get("icon_filename"),
    )


class SettingsRepository:
    """Репозиторий для чтения и записи настроек приложения в JSON."""

    def __init__(self, paths: AppPaths) -> None:
        self._paths = paths

    def load(self) -> Settings:
        """Читает настройки из файла и дополняет их дефолтными значениями."""
        raw = read_json(self._paths.settings_file, default={})
        return Settings(
            accent_color=str(raw.get("accent_color", Settings().accent_color)),
            theme=str(raw.get("theme", Settings().theme)),
            font_family=str(raw.get("font_family", Settings().font_family)),
        )

    def save(self, s: Settings) -> None:
        """Сохраняет объект Settings в JSON-файл."""
        write_json_atomic(self._paths.settings_file, asdict(s))


class CategoriesRepository:
    """Репозиторий для управления списком категорий."""

    def __init__(self, paths: AppPaths) -> None:
        self._paths = paths

    def load_all(self) -> list[Category]:
        """Возвращает все сохранённые категории из JSON-файла."""
        raw = read_json(self._paths.categories_file, default=[])
        if not isinstance(raw, list):
            return []
        return [_category_from_json(x) for x in raw if isinstance(x, dict)]

    def save_all(self, cats: Iterable[Category]) -> None:
        """Перезаписывает JSON-файл полным списком переданных категорий."""
        write_json_atomic(
            self._paths.categories_file, [_category_to_json(c) for c in cats]
        )

    def add(
        self, name: str, color: str, *, icon_source_path: Optional[Path]
    ) -> Category:
        """Создаёт новую категорию и сохраняет её.

        Дополнительно, если указан путь к иконке, копирует файл в директорию
        `icons_dir` и сохраняет только имя файла в поле `icon_filename`.
        """
        cats = self.load_all()
        cat_id = uuid.uuid4().hex

        icon_filename: Optional[str] = None
        if icon_source_path:
            suffix = icon_source_path.suffix.lower() or ".png"
            icon_filename = f"{cat_id}{suffix}"
            dest = self._paths.icons_dir / icon_filename
            self._paths.icons_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(icon_source_path, dest)

        cat = Category(
            id=cat_id, name=name.strip(), color=color, icon_filename=icon_filename
        )
        cats.append(cat)
        self.save_all(cats)
        return cat

    def delete_by_id(self, cat_id: str) -> bool:
        """Удаляет категорию по ID из JSON и файл иконки в icons_dir, если был."""
        cats = self.load_all()
        removed = next((c for c in cats if c.id == cat_id), None)
        if removed is None:
            return False
        remaining = [c for c in cats if c.id != cat_id]
        if removed.icon_filename:
            icon_path = self._paths.icons_dir / removed.icon_filename
            if icon_path.exists():
                icon_path.unlink()
        self.save_all(remaining)
        return True


class TasksRepository:
    """Репозиторий задач с постраничным хранением в JSON.

    Задачи лежат в нескольких файлах page_0001.json, page_0002.json и т.д.
    Это позволяет подгружать их по страницам (infinite scroll), а не
    загружать все задачи сразу в память.
    """

    def __init__(self, paths: AppPaths, *, page_size: int = 25) -> None:
        self._paths = paths
        self._page_size = page_size

    def page_size(self) -> int:
        return self._page_size

    def _page_files(self) -> list[Path]:
        """Возвращает отсортированный список файлов страниц с задачами."""
        self._paths.tasks_pages_dir.mkdir(parents=True, exist_ok=True)
        files = sorted(self._paths.tasks_pages_dir.glob("page_*.json"))
        return files

    def _next_page_path(self) -> Path:
        """Определяет путь к следующему файлу страницы."""
        files = self._page_files()
        if not files:
            return self._paths.tasks_pages_dir / "page_0001.json"
        last = files[-1].stem  # page_0001
        try:
            n = int(last.split("_", 1)[1])
        except Exception:
            n = len(files)
        return self._paths.tasks_pages_dir / f"page_{n + 1:04d}.json"

    def load_page(self, page_index: int) -> list[Task]:
        """Загружает одну страницу задач по индексу (0-based).

        Если индекс вне диапазона, возвращает пустой список.
        """
        files = self._page_files()
        if page_index < 0 or page_index >= len(files):
            return []
        raw = read_json(files[page_index], default=[])
        if not isinstance(raw, list):
            return []
        return [_task_from_json(x) for x in raw if isinstance(x, dict)]

    def load_all(self) -> list[Task]:
        """Загружает все задачи из всех страниц (без сортировки)."""
        tasks: list[Task] = []
        for i in range(self.page_count()):
            tasks.extend(self.load_page(i))
        return tasks

    def page_count(self) -> int:
        """Возвращает текущее количество файлов-страниц."""
        return len(self._page_files())

    def add(
        self,
        title: str,
        *,
        category_id: Optional[str],
        due: Optional[date],
        priority: int = 0,
        important: bool = False,
    ) -> Task:
        """Создаёт новую задачу и добавляет её в последнюю страницу.

        Если последняя страница заполнена (page_size), создаётся новый файл.
        """
        task = Task(
            id=uuid.uuid4().hex,
            title=title.strip(),
            category_id=category_id,
            due=due,
            priority=int(priority),
            important=bool(important),
            done=False,
            done_at=None,
        )

        files = self._page_files()
        if not files:
            path = self._paths.tasks_pages_dir / "page_0001.json"
            write_json_atomic(path, [_task_to_json(task)])
            return task

        last_path = files[-1]
        raw = read_json(last_path, default=[])
        if not isinstance(raw, list):
            raw = []

        if len(raw) >= self._page_size:
            new_path = self._next_page_path()
            write_json_atomic(new_path, [_task_to_json(task)])
            return task

        raw.append(_task_to_json(task))
        write_json_atomic(last_path, raw)
        return task

    def ensure_seed_data(self) -> None:
        """Создаёт пару стартовых задач при первом запуске приложения."""
        if self.page_count() > 0:
            return
        self.add("Welcome to TaskManagerApp", category_id=None, due=_today())
        self.add("Pin the sidebar to keep it open", category_id=None, due=None)

    def set_done(self, task_id: str, done: bool) -> bool:
        """Обновляет флаг выполнения задачи в JSON без загрузки всех задач.

        Стратегия: последовательно сканируем все страницы, находим нужную
        задачу по ID, меняем поле `done` и перезаписываем этот один файл.

        Возвращает:
            True, если задача была найдена и обновлена, иначе False.
        """
        files = self._page_files()
        for path in files:
            raw = read_json(path, default=[])
            if not isinstance(raw, list):
                continue
            updated = False
            for item in raw:
                if not isinstance(item, dict):
                    continue
                if str(item.get("id")) == task_id:
                    item["done"] = bool(done)
                    item["done_at"] = (
                        datetime.now(timezone.utc).isoformat() if done else None
                    )
                    updated = True
                    break
            if updated:
                write_json_atomic(path, raw)
                return True
        return False

    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Возвращает задачу по ID или None, если не найдена."""
        files = self._page_files()
        for path in files:
            raw = read_json(path, default=[])
            if not isinstance(raw, list):
                continue
            for item in raw:
                if not isinstance(item, dict):
                    continue
                if str(item.get("id")) == task_id:
                    return _task_from_json(item)
        return None

    def update(
        self,
        task_id: str,
        *,
        title: str,
        category_id: Optional[str],
        due: Optional[date],
        priority: int,
        important: bool,
    ) -> bool:
        """Обновляет поля задачи по ID."""
        files = self._page_files()
        for path in files:
            raw = read_json(path, default=[])
            if not isinstance(raw, list):
                continue
            updated = False
            for item in raw:
                if not isinstance(item, dict):
                    continue
                if str(item.get("id")) == task_id:
                    item["title"] = title.strip()
                    item["category_id"] = category_id
                    item["due"] = due.isoformat() if due else None
                    item["priority"] = int(priority)
                    item["important"] = bool(important)
                    updated = True
                    break
            if updated:
                write_json_atomic(path, raw)
                return True
        return False

    def set_important(self, task_id: str, important: bool) -> bool:
        """Обновляет флаг важности задачи по ID."""
        files = self._page_files()
        for path in files:
            raw = read_json(path, default=[])
            if not isinstance(raw, list):
                continue
            updated = False
            for item in raw:
                if not isinstance(item, dict):
                    continue
                if str(item.get("id")) == task_id:
                    item["important"] = bool(important)
                    updated = True
                    break
            if updated:
                write_json_atomic(path, raw)
                return True
        return False

    def delete(self, task_id: str) -> bool:
        """Удаляет задачу по ID."""
        files = self._page_files()
        for path in files:
            raw = read_json(path, default=[])
            if not isinstance(raw, list):
                continue
            before = len(raw)
            raw = [
                x
                for x in raw
                if not (isinstance(x, dict) and str(x.get("id")) == task_id)
            ]
            if len(raw) != before:
                write_json_atomic(path, raw)
                return True
        return False

    def delete_all_by_category_id(self, category_id: str) -> int:
        """Удаляет все задачи с указанной категорией со всех страниц. Возвращает число удалённых задач."""
        removed = 0
        for path in self._page_files():
            raw = read_json(path, default=[])
            if not isinstance(raw, list):
                continue
            new_raw: list = []
            for item in raw:
                if not isinstance(item, dict):
                    new_raw.append(item)
                    continue
                if str(item.get("category_id")) == category_id:
                    removed += 1
                    continue
                new_raw.append(item)
            if len(new_raw) != len(raw):
                write_json_atomic(path, new_raw)
        return removed
