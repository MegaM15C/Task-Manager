# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec-файл для сборки Task Manager в один исполняемый файл.

Запускается автоматически через build.py. При необходимости вызывать вручную:
    pyinstaller task-manager.spec
"""

from pathlib import Path

ROOT = Path(SPECPATH)

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "resources"), "resources"),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "platformdirs",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="task-manager",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(ROOT / "resources" / "icons" / "app_icon.png"),
)
