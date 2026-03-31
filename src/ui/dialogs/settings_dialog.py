from __future__ import annotations

"""Диалог настроек приложения (акцент, тема, шрифт)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QColorDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from typing import Callable, Optional

from src.core.models import Settings
from src.ui.widgets.overlay_dialog import OverlayDialog
from src.utils.dialog import DialogHelperMixin

class SettingsDialog(OverlayDialog, DialogHelperMixin):
    """Диалог «Настройки» поверх главного окна."""

    def __init__(
        self,
        parent,
        settings: Settings,
        *,
        on_export: Optional[Callable[[str], None]] = None,
        on_import: Optional[Callable[[str], bool]] = None,
    ) -> None:
        """Инициализирует элементы управления на основе текущих настроек."""
        super().__init__(parent, title="Настройки")
        self._settings = settings
        self._on_export = on_export
        self._on_import = on_import

        self._accent_btn = QPushButton("Выбрать цвет", self)
        self._accent_btn.setCursor(Qt.PointingHandCursor)
        self._accent_btn.clicked.connect(self._pick_accent)

        self._accent_preview = QPushButton("", self)
        self._accent_preview.setFixedSize(28, 28)
        self._accent_preview.setCursor(Qt.PointingHandCursor)
        self._accent_preview.clicked.connect(self._pick_accent)
        self._accent_preview.setObjectName("AccentPreview")

        self._theme = QComboBox(self)
        self._theme.addItems(["Светлая", "Тёмная"])

        self._font = QComboBox(self)
        self._font.addItems(["Ubuntu Sans", "Inter", "Roboto", "Segoe UI"])
        if settings.font_family:
            i = self._font.findText(settings.font_family)
            if i >= 0:
                self._font.setCurrentIndex(i)

        self.body.addLayout(
            self._row(
                "Акцентный цвет",
                "Выбор акцентного цвета, используемого в приложении",
                control_layout=self._accent_control(),
            )
        )
        self.body.addWidget(self._divider())
        self.body.addLayout(
            self._row(
                "Основная тема",
                "Выбор основной цветовой схемы оформления Активa",
                control_widget=self._theme,
            )
        )
        self.body.addWidget(self._divider())
        self.body.addLayout(
            self._row(
                "Основной шрифт",
                "Выбор основного шрифта интерфейса и текста в Активa",
                control_widget=self._font,
            )
        )

        self.body.addWidget(self._divider())

        self._export_btn = QPushButton("Экспорт…", self)
        self._export_btn.setCursor(Qt.PointingHandCursor)
        self._export_btn.clicked.connect(self._export_clicked)
        self._export_btn.setEnabled(self._on_export is not None)

        self._import_btn = QPushButton("Импорт…", self)
        self._import_btn.setCursor(Qt.PointingHandCursor)
        self._import_btn.clicked.connect(self._import_clicked)
        self._import_btn.setEnabled(self._on_import is not None)

        self.body.addLayout(
            self._row(
                "Экспорт и импорт",
                "Сохранение и восстановление всех настроек и задач из файла",
                control_layout=self._export_import_controls(),
            )
        )

        self._apply_initial()

        self._save = QPushButton("Сохранить", self)
        self._save.setObjectName("AcceptButton")
        self._save.clicked.connect(self.accept)
        cancel = QPushButton("Отменить", self)
        cancel.clicked.connect(self.reject)

        self.footer.addStretch(1)
        self.footer.addWidget(cancel)
        self.footer.addWidget(self._save)


    def _accent_control(self) -> QHBoxLayout:
        """Возвращает layout с кнопкой выбора цвета и кругом-превью."""
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)
        h.addWidget(self._accent_btn)
        h.addWidget(self._accent_preview)
        return h

    def _apply_initial(self) -> None:
        """Применяет стартовые значения акцентного цвета и темы."""
        self._set_accent_preview(self._settings.accent_color)
        self._theme.setCurrentIndex(1 if self._settings.theme == "dark" else 0)

    def _set_accent_preview(self, hex_color: str) -> None:
        """Обновляет цвет круга-превью для акцентного цвета."""
        self._accent_preview.setStyleSheet(
            f"""
            QPushButton#AccentPreview {{
                background: {hex_color};
            }}
            """
        )

    def _pick_accent(self) -> None:
        """Открывает цветовой диалог и обновляет текущий акцентный цвет."""
        c = QColorDialog.getColor(QColor(self._settings.accent_color), self, "Акцентный цвет")
        #print(c.name())
        if not c.isValid():
            return
        self._settings = Settings(
            accent_color=c.name(),
            theme=self._settings.theme,
            font_family=self._settings.font_family,
        )
        self._set_accent_preview(self._settings.accent_color)

    def result_settings(self) -> Settings:
        """Возвращает объект Settings, собранный из введённых пользователем значений."""
        theme = "dark" if self._theme.currentText() == "Тёмная" else "light"
        return Settings(
            accent_color=self._settings.accent_color,
            theme=theme,
            font_family=self._font.currentText(),
        )

    def _export_import_controls(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)
        h.addWidget(self._export_btn)
        h.addWidget(self._import_btn)
        return h

    def _export_clicked(self) -> None:
        if self._on_export is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт данных",
            "task_manager_backup.zip",
            "Backup (*.zip)",
        )
        if not path:
            return
        self._on_export(path)

    def _import_clicked(self) -> None:
        if self._on_import is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Импорт данных",
            "",
            "Backup (*.zip)",
        )
        if not path:
            return
        ok = self._on_import(path)
        # Если импорт успешен, закрываем диалог, чтобы пользователь не мог
        # "пересохранить" старые значения поверх импортированных.
        if ok:
            self.reject()

