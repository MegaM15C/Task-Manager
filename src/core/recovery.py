from __future__ import annotations

"""Обнаружение и восстановление повреждённых файлов хранилища."""

import json
import logging
import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from .paths import AppPaths

logger = logging.getLogger(__name__)


class StorageRecoveryManager:
    """Проверяет целостность JSON-хранилища и выполняет восстановление."""

    def __init__(self, paths: AppPaths) -> None:
        self._paths = paths

    def validate(self) -> list[Path]:
        """Возвращает список существующих, но нечитаемых JSON-файлов.

        Отсутствующий файл — не ошибка (первый запуск).
        Существующий файл с невалидным содержимым — повреждение.
        """
        candidates: list[Path] = [
            self._paths.settings_file,
            self._paths.categories_file,
        ]
        if self._paths.tasks_pages_dir.exists():
            candidates.extend(
                sorted(self._paths.tasks_pages_dir.glob("page_*.json"))
            )

        corrupted: list[Path] = []
        for path in candidates:
            if not path.exists() or not path.is_file():
                continue
            try:
                with path.open("r", encoding="utf-8") as f:
                    json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
                logger.warning("Повреждённый файл хранилища: %s — %s", path, exc)
                corrupted.append(path)

        return corrupted

    def backup_and_reset(self) -> Path:
        """Перемещает data_dir в резервную директорию и пересоздаёт структуру.

        Возвращает Path к директории с резервной копией.
        Выбрасывает OSError при невозможности выполнить операцию.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self._paths.config_dir / f"data_backup_{ts}"

        if self._paths.data_dir.exists():
            logger.info(
                "Перемещение повреждённого хранилища: %s → %s",
                self._paths.data_dir,
                backup_dir,
            )
            # shutil.move работает через разные файловые системы, Path.rename — нет
            shutil.move(str(self._paths.data_dir), str(backup_dir))
        else:
            backup_dir.mkdir(parents=True, exist_ok=True)

        self._paths.ensure()
        logger.info("Хранилище успешно пересоздано. Резервная копия: %s", backup_dir)
        return backup_dir

    def open_data_directory(self) -> None:
        """Открывает директорию данных в системном файловом менеджере.

        Выбрасывает OSError / subprocess.CalledProcessError при неудаче.
        """
        path = self._paths.data_dir
        system = platform.system()
        if system == "Windows":
            os.startfile(str(path))
        elif system == "Darwin":
            subprocess.run(["open", str(path)], check=True)
        else:
            subprocess.run(["xdg-open", str(path)], check=True)
        logger.info("Открыта директория хранилища: %s", path)
