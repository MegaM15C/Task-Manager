import sys
import logging
import platform
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon

from src.core.paths import AppPaths
from src.core.recovery import StorageRecoveryManager
from src.ui.dialogs.storage_error_dialog import StorageErrorDialog
from src.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def _setup_logging(log_file: Path) -> None:
    """INFO → stderr, DEBUG → файл app.log."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    root.addHandler(console)

    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except OSError as exc:
        # Не можем писать лог-файл — продолжаем только с консолью
        logging.getLogger(__name__).warning(
            "Не удалось открыть лог-файл %s: %s", log_file, exc
        )


def setup_app(app: QApplication) -> None:
    icon_path = "resources/icons/app_icon.png"
    app.setWindowIcon(QIcon(icon_path))
    app.setApplicationName("task-manager")

    system = platform.system()
    if system == "Windows":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "task.manager.app"
        )
    elif system == "Linux":
        app.setDesktopFileName("task-manager")


def main() -> int:
    # QApplication создаётся первым — без него QMessageBox работать не будет
    app = QApplication(sys.argv)
    setup_app(app)

    paths = AppPaths()
    _setup_logging(paths.config_dir / "app.log")
    logger.info("Запуск приложения")

    # Создаём директории хранилища — может упасть при проблемах с правами
    try:
        paths.ensure()
    except OSError as exc:
        logger.critical("Не удалось создать директории хранилища: %s", exc)
        QMessageBox.critical(
            None,
            "Критическая ошибка",
            f"Не удалось создать директории данных приложения:\n\n{exc}\n\n"
            "Проверьте права доступа к домашней директории.",
        )
        return 1

    # Проверяем целостность JSON-файлов перед созданием главного окна
    recovery = StorageRecoveryManager(paths)
    corrupted = recovery.validate()

    if corrupted:
        logger.warning(
            "Обнаружено повреждённых файлов: %d — %s",
            len(corrupted),
            [p.name for p in corrupted],
        )
        dlg = StorageErrorDialog(recovery, corrupted)
        result = dlg.exec()
        if result != StorageErrorDialog.DialogCode.Accepted:
            logger.info("Пользователь выбрал выход из диалога восстановления")
            return 0
        # Пользователь нажал "Пересоздать" — продолжаем запуск с чистым хранилищем

    try:
        window = MainWindow()
    except Exception as exc:
        logger.critical("Не удалось создать главное окно: %s", exc, exc_info=True)
        QMessageBox.critical(
            None,
            "Критическая ошибка",
            f"Не удалось запустить приложение:\n\n{exc}",
        )
        return 1

    window.show()
    logger.info("Приложение запущено")
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
