from __future__ import annotations

"""Экспорт/импорт всех данных приложения (настройки, категории, задачи, иконки).

Формат экспорта: zip-архив со структурой:
  - meta.json
  - data/settings.json
  - data/categories.json
  - data/tasks_pages/page_0001.json ...
  - icons/<files...>
"""

import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .paths import AppPaths


class BackupError(RuntimeError):
    pass


def _zip_write_file(zf: zipfile.ZipFile, *, src: Path, arcname: str) -> None:
    if not src.exists() or not src.is_file():
        return
    zf.write(src, arcname=arcname)


def _iter_files(dir_path: Path) -> Iterable[Path]:
    if not dir_path.exists() or not dir_path.is_dir():
        return []
    return [p for p in dir_path.rglob("*") if p.is_file()]


def export_all(paths: AppPaths, dest_zip: Path) -> None:
    """Экспортирует все данные приложения в zip-архив."""
    dest_zip = Path(dest_zip)
    dest_zip.parent.mkdir(parents=True, exist_ok=True)

    meta = {
        "format": "task-manager-backup",
        "version": 1,
        "app_name": paths.app_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "included": {
            "settings": True,
            "categories": True,
            "tasks_pages": True,
            "icons": True,
        },
    }

    tmp = dest_zip.with_suffix(dest_zip.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()

    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

        _zip_write_file(zf, src=paths.settings_file, arcname="data/settings.json")
        _zip_write_file(zf, src=paths.categories_file, arcname="data/categories.json")

        for p in sorted(paths.tasks_pages_dir.glob("page_*.json")):
            _zip_write_file(zf, src=p, arcname=f"data/tasks_pages/{p.name}")

        for p in sorted(_iter_files(paths.icons_dir)):
            rel = p.relative_to(paths.icons_dir).as_posix()
            _zip_write_file(zf, src=p, arcname=f"icons/{rel}")

    tmp.replace(dest_zip)


def _is_safe_member(name: str) -> bool:
    # Prevent Zip Slip / path traversal.
    if not name or name.endswith("/"):
        return True
    p = Path(name)
    if p.is_absolute():
        return False
    if any(part in ("..", "") for part in p.parts):
        return False
    return True


def _extract_selected(
    zf: zipfile.ZipFile, *, members: list[str], dest_dir: Path
) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for name in members:
        if not _is_safe_member(name):
            raise BackupError(f"Небезопасный путь в архиве: {name!r}")
        if name.endswith("/"):
            continue
        target = dest_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(name, "r") as src, target.open("wb") as out:
            shutil.copyfileobj(src, out)


def import_all(paths: AppPaths, src_zip: Path) -> None:
    """Импортирует все данные из zip-архива, заменяя текущие данные приложения."""
    src_zip = Path(src_zip)
    if not src_zip.exists() or not src_zip.is_file():
        raise BackupError("Файл импорта не найден.")

    with zipfile.ZipFile(src_zip, "r") as zf:
        names = zf.namelist()
        if "meta.json" not in names:
            raise BackupError("Некорректный архив: отсутствует meta.json.")

        # meta validation (soft)
        try:
            raw_meta = json.loads(zf.read("meta.json").decode("utf-8"))
        except Exception as e:
            raise BackupError("Некорректный архив: meta.json повреждён.") from e
        if (
            not isinstance(raw_meta, dict)
            or raw_meta.get("format") != "task-manager-backup"
        ):
            raise BackupError("Некорректный архив: неизвестный формат.")

        wanted = [n for n in names if n.startswith(("data/", "icons/"))]

        with tempfile.TemporaryDirectory(prefix="taskmgr_import_") as td:
            staging = Path(td)
            _extract_selected(zf, members=wanted, dest_dir=staging)

            new_data = staging / "data"
            new_icons = staging / "icons"
            if not new_data.exists():
                raise BackupError("Некорректный архив: отсутствует папка data/.")
            if not new_icons.exists():
                new_icons.mkdir(parents=True, exist_ok=True)

            # Ensure target dirs exist before swap.
            paths.ensure()

            # Swap directories atomically-ish (best effort).
            backup_root = (
                paths.config_dir
                / f"_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            )
            backup_root.mkdir(parents=True, exist_ok=True)
            if paths.data_dir.exists():
                shutil.move(str(paths.data_dir), str(backup_root / "data"))
            if paths.icons_dir.exists():
                shutil.move(str(paths.icons_dir), str(backup_root / "icons"))

            shutil.copytree(new_data, paths.data_dir, dirs_exist_ok=True)
            shutil.copytree(new_icons, paths.icons_dir, dirs_exist_ok=True)
