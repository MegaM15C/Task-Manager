from __future__ import annotations

"""Диалог настроек приложения (акцент, тема, шрифт)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox, QColorDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from src.core.models import Settings
from src.ui.widgets.overlay_dialog import OverlayDialog
from src.utils.dialog import DialogHelperMixin

class SettingsDialog(OverlayDialog, DialogHelperMixin):
    """Диалог «Настройки» поверх главного окна."""

    def __init__(self, parent, settings: Settings) -> None:
        """Инициализирует элементы управления на основе текущих настроек."""
        super().__init__(parent, title="Настройки")
        self._settings = settings

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
    def apply_theme_tokens(self, tokens: ThemeTokens) -> None:
        self._pin_hover.set_tokens(tokens)
        self._theme_hover.set_tokens(tokens)

