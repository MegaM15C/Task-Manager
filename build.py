#!/usr/bin/env python3
"""Сборочный скрипт: создаёт дистрибутивный пакет под текущую платформу.

Linux  → dist/task-manager  +  dist/task-manager_<version>_amd64.deb
Windows → dist/task-manager.exe

Использование:
    python build.py              # автоопределение платформы
    python build.py --clean      # удалить build/ и dist/ перед сборкой
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
VERSION = "0.8.0"
APP_NAME = "task-manager"


def run(cmd: list[str | Path], **kwargs) -> None:
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kwargs)


def clean() -> None:
    for d in (DIST, BUILD):
        if d.exists():
            shutil.rmtree(d)
            print(f"Удалена директория: {d}")


def build_pyinstaller() -> None:
    """Запускает PyInstaller и создаёт одиночный исполняемый файл."""
    run([sys.executable, "-m", "PyInstaller", "--clean", "task-manager.spec"])


def build_deb(binary: Path) -> Path:
    """Упаковывает Linux-бинарник в .deb-пакет формата Debian."""
    pkg_root = BUILD / "deb-pkg"
    if pkg_root.exists():
        shutil.rmtree(pkg_root)

    # Стандартная структура .deb
    bin_dir = pkg_root / "usr" / "local" / "bin"
    icon_dir = pkg_root / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    apps_dir = pkg_root / "usr" / "share" / "applications"
    debian_dir = pkg_root / "DEBIAN"
    for d in (bin_dir, icon_dir, apps_dir, debian_dir):
        d.mkdir(parents=True)

    # Бинарник
    dest_bin = bin_dir / APP_NAME
    shutil.copy2(binary, dest_bin)
    dest_bin.chmod(0o755)

    # Иконка (берётся из исходников проекта)
    icon_src = ROOT / "resources" / "icons" / "app_icon.png"
    if icon_src.exists():
        shutil.copy2(icon_src, icon_dir / f"{APP_NAME}.png")

    # .desktop-файл
    (apps_dir / f"{APP_NAME}.desktop").write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Менеджер задач\n"
        "Name[en]=Task Manager\n"
        "Comment=Десктопный менеджер задач\n"
        "Comment[en]=Desktop task manager\n"
        f"Exec=/usr/local/bin/{APP_NAME}\n"
        f"Icon={APP_NAME}\n"
        "Categories=Office;ProjectManagement;\n"
        f"StartupWMClass={APP_NAME}\n"
        "StartupNotify=true\n"
        "Terminal=false\n",
        encoding="utf-8",
    )

    # DEBIAN/control
    (debian_dir / "control").write_text(
        f"Package: {APP_NAME}\n"
        f"Version: {VERSION}\n"
        "Architecture: amd64\n"
        "Maintainer: Developer MegaM15C (DNGRMXM)\n"
        "Depends: libgl1\n"
        "Section: office\n"
        "Priority: optional\n"
        "Description: Менеджер задач\n"
        " Десктопный менеджер задач с поддержкой категорий, приоритетов,\n"
        " дедлайнов и резервного копирования. Написан на Python / PySide6.\n",
        encoding="utf-8",
    )

    # DEBIAN/postinst — обновляем кэш иконок и базу .desktop после установки
    postinst = debian_dir / "postinst"
    postinst.write_text(
        "#!/bin/sh\n"
        "set -e\n"
        "gtk-update-icon-cache /usr/share/icons/hicolor 2>/dev/null || true\n"
        "update-desktop-database /usr/share/applications 2>/dev/null || true\n",
        encoding="utf-8",
    )
    postinst.chmod(0o755)

    deb_filename = f"{APP_NAME}_{VERSION}_amd64.deb"
    deb_path = DIST / deb_filename
    run(["dpkg-deb", "--build", "--root-owner-group", str(pkg_root), str(deb_path)])
    return deb_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Task Manager distributable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Примеры:\n"
            "  python build.py                    # авто-определение платформы\n"
            "  python build.py --platform linux   # принудительно Linux (.deb)\n"
            "  python build.py --platform windows # принудительно Windows (.exe)\n"
            "  python build.py --clean            # очистить артефакты перед сборкой\n"
        ),
    )
    parser.add_argument(
        "--platform",
        choices=["linux", "windows"],
        default=None,
        metavar="PLATFORM",
        help="Целевая платформа: linux | windows (по умолчанию — текущая ОС)",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Очистить build/ и dist/ перед сборкой"
    )
    args = parser.parse_args()

    if args.clean:
        clean()

    if args.platform:
        system = args.platform.capitalize()  # "linux" → "Linux", "windows" → "Windows"
    else:
        system = platform.system()

    print(f"\n{'='*50}")
    print(f"Сборка для платформы: {system}")
    if args.platform and args.platform.lower() != platform.system().lower():
        print("  ⚠ Целевая платформа отличается от текущей.")
        print("    PyInstaller собирает только под ОС, на которой запущен.")
        print("    Для кросс-компиляции используйте CI (GitHub Actions и др.).")
    print(f"{'='*50}\n")

    build_pyinstaller()

    if system == "Linux":
        binary = DIST / APP_NAME
        if not binary.exists():
            print(f"Ошибка: бинарник не найден после сборки: {binary}", file=sys.stderr)
            return 1
        deb_path = build_deb(binary)
        print(f"\n✓ Артефакты сборки:")
        print(f"  {binary.relative_to(ROOT)}")
        print(f"  {deb_path.relative_to(ROOT)}")

    elif system == "Windows":
        exe_path = DIST / f"{APP_NAME}.exe"
        print(f"\n✓ Артефакт сборки:")
        print(f"  {exe_path.relative_to(ROOT)}")

    else:
        print(f"Платформа '{system}' не поддерживается этим скриптом.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
