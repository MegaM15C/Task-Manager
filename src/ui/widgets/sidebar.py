from __future__ import annotations

"""Левый сайдбар с навигацией по видам и категориям задач."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.core.models import Category


class Sidebar(QFrame):
    """Сайдбар со списком видов (все/дедлайны/важное) и пользовательских категорий."""

    view_selected = Signal(str)  # view key: all, deadlines, important, category:<id>
    add_category_requested = Signal()
    settings_requested = Signal()
    theme_toggled = Signal(bool)  # True => dark

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(300)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Меню", self)
        title.setObjectName("SidebarTitle")
        top.addWidget(title)
        top.addStretch(1)

        self.pin_btn = QToolButton(self)
        #self.pin_btn.setCheckable(True)
        self.pin_btn.setText("📌")
        self.pin_btn.setToolTip("Закрепить сайдбар")
        self.pin_btn.setObjectName("PinButton")
        self.pin_btn.setFixedSize(34, 34)
        #self.pin_btn.clicked.connect(self.Sidebar._on_pin_toggled)
        top.addWidget(self.pin_btn)

        root.addLayout(top)

        self._nav_all = QPushButton("🗒  Все задачи", self)
        self._nav_deadlines = QPushButton("📅  Дедлайны", self)
        self._nav_important = QPushButton("⭐  Важное", self)
        for b in (self._nav_all, self._nav_deadlines, self._nav_important):
            b.setObjectName("NavButton")
            b.setCursor(Qt.PointingHandCursor)

        self._nav_all.clicked.connect(lambda: self.view_selected.emit("all"))
        self._nav_deadlines.clicked.connect(lambda: self.view_selected.emit("deadlines"))
        self._nav_important.clicked.connect(lambda: self.view_selected.emit("important"))

        root.addWidget(self._nav_all)
        root.addWidget(self._nav_deadlines)
        root.addWidget(self._nav_important)

        root.addSpacing(4)
        cats_lbl = QLabel("Категории", self)
        cats_lbl.setObjectName("SidebarSectionLabel")
        root.addWidget(cats_lbl)

        self._cats_container = QWidget(self)
        self._cats_layout = QVBoxLayout(self._cats_container)
        self._cats_layout.setContentsMargins(0, 0, 0, 0)
        self._cats_layout.setSpacing(8)
        self._cats_layout.addStretch(1)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self._cats_container)
        root.addWidget(scroll, 1)

        add_cat = QPushButton("+ Добавить категорию", self)
        add_cat.setObjectName("AddCategoryButton")
        add_cat.clicked.connect(self.add_category_requested.emit)
        root.addWidget(add_cat)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)

        self._theme_btn = QToolButton(self)
        self._theme_btn.setCheckable(True)
        self._theme_btn.setText("🌙")
        self._theme_btn.setToolTip("Переключить тему")
        self._theme_btn.setObjectName("ThemeButton")
        self._theme_btn.setFixedSize(42, 34)
        self._theme_btn.toggled.connect(self.theme_toggled.emit)
        bottom.addWidget(self._theme_btn)

        bottom.addStretch(1)

        gear = QToolButton(self)
        gear.setText("⚙")
        gear.setToolTip("Настройки")
        gear.setObjectName("SettingsButton")
        gear.setFixedSize(42, 34)
        gear.clicked.connect(self.settings_requested.emit)
        bottom.addWidget(gear)

        root.addLayout(bottom)
        # Visual styling is applied globally from `src/ui/theme.py` QSS so it can
        # react to theme changes (light/dark) consistently.

    def set_theme_checked(self, *, dark: bool) -> None:
        """Программно выставляет состояние переключателя темы."""
        self._theme_btn.blockSignals(True)
        self._theme_btn.setChecked(dark)
        self._theme_btn.setText("🌙" if dark else "☀")
        self._theme_btn.blockSignals(False)

    def set_categories(self, categories: list[Category]) -> None:
        """Обновляет список кнопок категорий на панели."""
        # удаляем старые кнопки (статический отступ/стретч пересоздадим ниже)
        while self._cats_layout.count() > 0:
            item = self._cats_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                # spacer/stretch
                pass

        for c in categories:
            b = QPushButton(f"🏷  {c.name}", self._cats_container)
            b.setObjectName("NavButton")
            b.setStyleSheet(f"QPushButton#NavButton{{ border-left: 6px solid {c.color}; }}")
            b.clicked.connect(lambda _=False, cid=c.id: self.view_selected.emit(f"category:{cid}"))
            self._cats_layout.addWidget(b)

        self._cats_layout.addStretch(1)

