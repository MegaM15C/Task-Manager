from __future__ import annotations

"""Диалог восстановления хранилища — показывается до создания MainWindow."""

import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.core.recovery import StorageRecoveryManager

logger = logging.getLogger(__name__)


class StorageErrorDialog(QDialog):
    """Показывается при старте, если обнаружены повреждённые файлы хранилища.

    Не требует родительского виджета — MainWindow в этот момент ещё не создан.
    """

    def __init__(self, manager: StorageRecoveryManager, corrupted: list[Path]) -> None:
        super().__init__(None)
        self._manager = manager

        self.setWindowTitle("Ошибка хранилища данных")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        # --- Заголовок ---
        title = QLabel("Обнаружены повреждённые файлы данных", self)
        title.setStyleSheet("font-size: 15px; font-weight: 800;")
        root.addWidget(title)

        # --- Описание ---
        desc = QLabel(
            "Приложение не может загрузить данные хранилища — один или несколько "
            "JSON-файлов повреждены. Выберите действие для восстановления работы.",
            self,
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888888;")
        root.addWidget(desc)

        # --- Список повреждённых файлов ---
        files_label = QLabel("Повреждённые файлы:", self)
        files_label.setStyleSheet("font-weight: 700; margin-top: 4px;")
        root.addWidget(files_label)

        for path in corrupted:
            item = QLabel(f"  • {path.name}", self)
            item.setStyleSheet("color: #E05252; font-family: monospace; font-size: 13px;")
            root.addWidget(item)

        # --- Разделитель ---
        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #444444; margin-top: 4px; margin-bottom: 4px;")
        root.addWidget(sep)

        # --- Кнопки (вертикально, чтобы не перепутать) ---
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self._reset_btn = QPushButton("Пересоздать хранилище задач", self)
        self._reset_btn.setStyleSheet(
            "QPushButton { font-weight: 700; padding: 10px 16px; }"
        )
        self._reset_btn.setToolTip(
            "Переместить повреждённые файлы в резервную папку и создать чистое хранилище"
        )
        self._reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(self._reset_btn)

        open_btn = QPushButton("Открыть папку хранилища", self)
        open_btn.setStyleSheet("QPushButton { padding: 10px 16px; }")
        open_btn.setToolTip(
            "Открыть директорию с файлами данных в файловом менеджере для ручного восстановления"
        )
        open_btn.clicked.connect(self._on_open_folder)
        btn_layout.addWidget(open_btn)

        # Разделитель перед "Выйти" — визуально отделяет деструктивное действие
        spacer_line = QFrame(self)
        spacer_line.setFrameShape(QFrame.Shape.HLine)
        spacer_line.setStyleSheet("color: #444444;")
        btn_layout.addWidget(spacer_line)

        exit_btn = QPushButton("Выйти", self)
        exit_btn.setStyleSheet("QPushButton { padding: 10px 16px; color: #888888; }")
        exit_btn.clicked.connect(self.reject)
        btn_layout.addWidget(exit_btn)

        root.addLayout(btn_layout)

    def _on_reset(self) -> None:
        """Выполняет backup_and_reset(), уведомляет об успехе, принимает диалог."""
        self._reset_btn.setEnabled(False)
        self._reset_btn.setText("Пересоздаём хранилище…")

        try:
            backup_path = self._manager.backup_and_reset()
        except OSError as exc:
            logger.error("backup_and_reset завершился с ошибкой: %s", exc)
            self._reset_btn.setEnabled(True)
            self._reset_btn.setText("Пересоздать хранилище задач")
            QMessageBox.critical(
                self,
                "Ошибка восстановления",
                f"Не удалось пересоздать хранилище:\n\n{exc}\n\n"
                "Проверьте права доступа к директории данных.",
            )
            return

        logger.info("Хранилище пересоздано. Резервная копия: %s", backup_path)
        QMessageBox.information(
            self,
            "Хранилище пересоздано",
            f"Данные успешно восстановлены.\n\n"
            f"Резервная копия повреждённых файлов сохранена в:\n{backup_path}",
        )
        self.accept()

    def _on_open_folder(self) -> None:
        """Открывает директорию хранилища. Не закрывает диалог при ошибке."""
        try:
            self._manager.open_data_directory()
        except Exception as exc:
            logger.error("Не удалось открыть папку хранилища: %s", exc)
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось открыть папку хранилища:\n\n{exc}",
            )
