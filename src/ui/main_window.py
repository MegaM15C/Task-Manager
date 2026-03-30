from __future__ import annotations

"""Главное окно приложения с сайдбаром и списком задач."""

from datetime import date, datetime, timedelta, timezone

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QCursor, QPixmap, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.models import Category, Settings, Task
from src.core.paths import AppPaths
from src.core.repositories import CategoriesRepository, SettingsRepository, TasksRepository
from src.ui.dialogs.create_category_dialog import CreateCategoryDialog
from src.ui.dialogs.create_task_dialog import CreateTaskDialog
from src.ui.dialogs.settings_dialog import SettingsDialog
from src.theme.theme import tokens_from_settings
from src.ui.styles.app import app_qss, font_from_settings
from src.ui.widgets.sidebar import Sidebar
from src.ui.widgets.task_item import TaskItemWidget
from src.utils.buttons import HoverEffect

from PySide6.QtCore import QPropertyAnimation, QEasingCurve

class SmoothScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()

        self._anim = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._anim.setDuration(400)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def wheelEvent(self, event):
        sb = self.verticalScrollBar()

        delta = event.angleDelta().y()

        # целевая позиция
        new_value = sb.value() - delta

        new_value = max(sb.minimum(), min(sb.maximum(), new_value))

        self._anim.stop()
        self._anim.setStartValue(sb.value())
        self._anim.setEndValue(new_value)
        self._anim.start()


class MainWindow(QMainWindow):
    """Главное окно приложения.

    Отвечает за:
    - инициализацию репозиториев и загрузку данных;
    - построение основного интерфейса (сайдбар + список задач);
    - обработку событий (инfinite scroll, фильтры, открытие диалогов).
    """

    def __init__(self) -> None:
        super().__init__()
        self._paths = AppPaths()
        self._paths.ensure()

        self._settings_repo = SettingsRepository(self._paths)
        self._cats_repo = CategoriesRepository(self._paths)
        self._tasks_repo = TasksRepository(self._paths, page_size=25)

        self._settings = self._settings_repo.load()
        self._tokens = tokens_from_settings(self._settings)
        self._categories: list[Category] = self._cats_repo.load_all()
        self._tasks_repo.ensure_seed_data()

        self._active_view_key = "all"
        self._page_index = 0
        self._loading = False
        self._view_tasks: list[Task] = []

        self._build_ui()
        self._apply_settings()
        self._reload_sidebar()
        self._reset_and_load_first_page()

    def _build_ui(self) -> None:
        """Создаёт все виджеты главного окна и настраивает layout-ы."""
        self.setWindowTitle("Менеджер задач")
        self.setFixedSize(1024, 768)

        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        # layout.setSpacing(10)

        self.sidebar = Sidebar(self._tokens, root)
        self.sidebar.pin_btn.toggled.connect(self._on_pin_toggled)
        self.sidebar.view_selected.connect(self._on_view_selected)
        self.sidebar.add_category_requested.connect(self._open_create_category)
        self.sidebar.category_delete_requested.connect(self._on_delete_category)
        self.sidebar.settings_requested.connect(self._open_settings)
        self.sidebar.theme_toggled.connect(self._on_theme_toggled)

        self._sidebar_container = QFrame(root)
        self._sidebar_container.setObjectName("SidebarContainer")
        s_l = QVBoxLayout(self._sidebar_container)
        s_l.setContentsMargins(0, 0, 0, 0)
        s_l.addWidget(self.sidebar)
        self._sidebar_container.setMaximumWidth(0)  # hidden by default
        layout.addWidget(self._sidebar_container)

        self._sidebar_anim = QPropertyAnimation(self._sidebar_container, b"maximumWidth", self)
        self._sidebar_anim.setDuration(180)
        self._sidebar_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._main = QFrame(root)
        self._main.setObjectName("MainArea")
        self._main.setFixedHeight(750)
        # self._main.setStyleSheet('border: 1px solid #000000') # Debug: показывает все границы элементов
        m = QVBoxLayout(self._main)
        m.setContentsMargins(18, 18, 18, 18)
        m.setSpacing(14)
        layout.addWidget(self._main, 1)

        # Оборачиваем header в QWidget
        header_widget = QWidget(self._main)
        header_widget.setObjectName("Header")
        #print(header_widget.styleSheet())

        # Создаём layout для header
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(8)

        # Иконка вида
        self._view_icon = QLabel("", self)
        self._view_icon.setFixedWidth(30)
        self._view_icon.setFixedHeight(30)
        self._icon_header = QPixmap('resources/icons/all_tasks.png')
        self._view_icon.setPixmap(self._icon_header)
        self._view_icon.setStyleSheet("font-size: 30px;")
        self._view_icon.setScaledContents(True)
        header_layout.addWidget(self._view_icon)

        # Заголовок вида
        self._view_title = QLabel("Все задачи", header_widget)
        self._view_title.setObjectName("ViewTitleHeader")
        self._view_icon.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self._view_title)

        # Раздвигаем содержимое
        header_layout.addStretch(1)

        # Кнопка "Добавить задачу"
        self.add_task = QPushButton("+ Добавить задачу", header_widget)
        self.hover_add_task = HoverEffect(self.add_task, tokens=self._tokens, anim_duration=750)
        self.add_task.setObjectName("PrimaryButton")
        self.add_task.clicked.connect(self._open_create_task)
        header_layout.addWidget(self.add_task)

        # Добавляем header_widget в основной layout
        m.addWidget(header_widget)

        self._scroll = SmoothScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)

        self._list_host = QWidget(self._scroll)
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(10)

        self._spinner = QLabel("Загружаем задачи…", self._list_host)
        self._spinner.setAlignment(Qt.AlignCenter)
        self._spinner.setObjectName("LoadingSpinner")
        self._spinner.hide()
        self._empty_state = QLabel("Задач не осталось, Вы хорошо постарались", self._list_host)
        self._empty_state.setAlignment(Qt.AlignCenter)
        self._empty_state.setObjectName("EmptyState")
        self._empty_state.hide()

        self._list_layout.addWidget(self._empty_state)
        self._list_layout.addWidget(self._spinner)
        self._list_layout.addStretch(1)
        self._scroll.setWidget(self._list_host)
        m.addWidget(self._scroll, 1)

        self._scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)

        # Hover-to-reveal region
        # Important: we install the filter on the *application* so mouse move
        # events from children still reach us (otherwise hover detection is flaky).
        self.setMouseTracking(True)
        root.setMouseTracking(True)
        self._main.setMouseTracking(True)
        self._scroll.viewport().setMouseTracking(True)
        # Use QApplication.instance() without importing at top to keep imports lean.
        from PySide6.QtWidgets import QApplication

        QApplication.instance().installEventFilter(self)

        self._pinned = False

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Отслеживает движение мыши, чтобы показывать/скрывать сайдбар."""
        if not self.isVisible():
            return super().eventFilter(watched, event)

        if event.type() == QEvent.MouseMove and not self._pinned:
            # We need window-local coordinates regardless of which child emitted the event.
            pos = self.mapFromGlobal(QCursor.pos())
            if 0 <= pos.x() <= 18:
                self._show_sidebar()
            elif pos.x() > self._sidebar_container.maximumWidth() + 20:
                self._hide_sidebar()
        return super().eventFilter(watched, event)

    def _show_sidebar(self) -> None:
        """Запускает анимацию раскрытия сайдбара."""
        if self._sidebar_container.maximumWidth() >= 300:
            return
        self._sidebar_anim.stop()
        self._sidebar_anim.setStartValue(self._sidebar_container.maximumWidth())
        # self._sidebar_anim.setEasingCurve(QEasingCurve.Type.InSine) # Анимация лагает
        self._sidebar_anim.setEndValue(300)
        self._sidebar_anim.setDuration(650)
        self._sidebar_anim.start()

    def _hide_sidebar(self) -> None:
        """Запускает анимацию скрытия сайдбара."""
        if self._sidebar_container.maximumWidth() <= 0:
            return
        self._sidebar_anim.stop()
        self._sidebar_anim.setStartValue(self._sidebar_container.maximumWidth())
        # self._sidebar_anim.setEasingCurve(QEasingCurve.Type.InSine) # Анимация лагает
        self._sidebar_anim.setEndValue(0)
        self._sidebar_anim.setDuration(650)
        self._sidebar_anim.start()

    def _on_pin_toggled(self, checked: bool) -> None:
        """Фиксирует сайдбар в раскрытом состоянии или возвращает режим hover."""
        self._pinned = checked
        self.sidebar.pin_btn.setText("")
        self.sidebar.pin_btn.setIcon(QPixmap()) 
        if checked:
            self.sidebar.pin_btn.setIcon(QPixmap("resources/icons/collapse.png")) 
            self._show_sidebar()
        else:
            self.sidebar.pin_btn.setIcon(QPixmap("resources/icons/expand.png")) 
            self._hide_sidebar()

    def _apply_settings(self) -> None:
        """Применяет текущие настройки темы/шрифта ко всему окну."""
        self._tokens = tokens_from_settings(self._settings)
        self.setStyleSheet(app_qss(self._tokens))
        self.sidebar.apply_theme_tokens(self._tokens)
        self.setFont(font_from_settings(self._settings))
        self.hover_add_task.set_tokens(self._tokens)
        self.sidebar.set_theme_checked(dark=self._settings.theme == "dark")

    def _reload_sidebar(self) -> None:
        """Обновляет список категорий в сайдбаре."""
        self._categories = self._cats_repo.load_all()
        self.sidebar.set_categories(self._categories)

    def _on_delete_category(self, category_id: str) -> None:
        """Удаляет категорию и все задачи в ней после подтверждения."""
        cat = next((x for x in self._categories if x.id == category_id), None)
        name = cat.name if cat else category_id
        result = QMessageBox.question(
            self,
            "Удалить категорию",
            f"Удалить категорию «{name}» и все задачи в ней? Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        self._tasks_repo.delete_all_by_category_id(category_id)
        self._cats_repo.delete_by_id(category_id)
        self._reload_sidebar()
        if self._active_view_key == f"category:{category_id}":
            self._on_view_selected("all")
        else:
            self._reset_and_load_first_page()

    def _open_settings(self) -> None:
        """Открывает диалог настроек и сохраняет новые значения при подтверждении."""
        dlg = SettingsDialog(self, self._settings)
        if dlg.exec() == QDialog.Accepted:
            self._settings = dlg.result_settings()
            self._settings_repo.save(self._settings)
            self._apply_settings()

    def _on_theme_toggled(self, dark: bool) -> None:
        """Обрабатывает переключатель темы в сайдбаре (light/dark)."""
        self._settings = Settings(
            accent_color=self._settings.accent_color,
            theme="dark" if dark else "light",
            font_family=self._settings.font_family,
        )
        self._settings_repo.save(self._settings)
        self._apply_settings()

    def _open_create_category(self) -> None:
        """Открывает диалог создания категории и добавляет её в JSON."""
        dlg = CreateCategoryDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        name, color, icon_path = dlg.result()
        if not name:
            return
        self._cats_repo.add(name, color, icon_source_path=icon_path)
        self._reload_sidebar()
        self._reset_and_load_first_page()

    def _open_create_task(self) -> None:
        """Открывает диалог создания задачи и сохраняет новую задачу."""
        dlg = CreateTaskDialog(self, categories=self._categories)
        if dlg.exec() != QDialog.Accepted:
            return
        title, cat_id, due, priority, important = dlg.result()
        if not title:
            return
        self._tasks_repo.add(
            title,
            category_id=cat_id,
            due=due,
            priority=priority,
            important=important,
        )
        self._reset_and_load_first_page()

    def _on_view_selected(self, key: str) -> None:
        """Меняет текущий фильтр списка задач."""
        self._active_view_key = key

        # очистка перед установкой
        self._view_icon.setPixmap(QPixmap())
        self._view_icon.setText("")

        if key == "all":
            self._view_icon.setPixmap(QPixmap('resources/icons/all_tasks.png'))
            self._view_title.setText("Все задачи")

        elif key == "deadlines":
            pixmap = QPixmap('resources/icons/deadline.png')
            #print(pixmap.isNull())  # диагностика если нужно
            self._view_icon.setPixmap(pixmap)
            self._view_title.setText("Дедлайны")

        elif key == "important":
            pixmap = QPixmap('resources/icons/important.png')            
            self._view_icon.setPixmap(pixmap)
            self._view_title.setText("Важное")

        elif key == "done":
            pixmap = QPixmap('resources/icons/completed_task.png')            
            self._view_icon.setPixmap(pixmap)
            self._view_title.setText("Выполненные")

        elif key.startswith("category:"):
            cid = key.split(":", 1)[1]
            c = next((x for x in self._categories if x.id == cid), None)
            self._view_icon.setText("🏷")
            self._view_title.setText(c.name if c else "Категория")

        self._reset_and_load_first_page()

    def _view_sort_key(self, t: Task) -> tuple:
        # Completed view: newest completed first
        if self._active_view_key == "done":
            done_at = t.done_at
            if isinstance(done_at, datetime):
                # Ensure timestamp() is safe across platforms.
                if done_at.tzinfo is None:
                    done_at = done_at.replace(tzinfo=timezone.utc)
                ts = done_at.timestamp()
            else:
                ts = 0.0
            return (-ts,)

        # Active views: higher priority first, then important, then earlier due dates
        due = t.due or date.max
        return (-int(t.priority or 0), -int(bool(t.important)), due.toordinal(), t.title)

    def _compute_view_tasks(self) -> list[Task]:
        tasks = self._tasks_repo.load_all()
        tasks = [t for t in tasks if self._passes_view_filter(t)]
        tasks.sort(key=self._view_sort_key)
        return tasks

    def _reset_and_load_first_page(self) -> None:
        """Сбрасывает список и загружает первую страницу задач согласно фильтру."""
        self._page_index = 0
        self._clear_task_widgets()
        self._view_tasks = self._compute_view_tasks()
        if not self._view_tasks:
            self._empty_state.show()
            return
        self._load_next_page()

    def _clear_task_widgets(self) -> None:
        """Удаляет все виджеты задач из layout-а и пересоздаёт строку со спиннером."""
        while self._list_layout.count() > 0:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                # spacer/stretch
                pass
        self._spinner = QLabel("Загружаем задачи…", self._list_host)
        self._spinner.setAlignment(Qt.AlignCenter)
        self._spinner.setObjectName("LoadingSpinner")
        self._spinner.hide()
        self._empty_state = QLabel("Задач не осталось, Вы хорошо постарались", self._list_host)
        self._empty_state.setAlignment(Qt.AlignCenter)
        self._empty_state.setObjectName("EmptyState")
        self._empty_state.hide()
        self._list_layout.addWidget(self._empty_state)
        self._list_layout.addWidget(self._spinner)
        self._list_layout.addStretch(1)

    def _on_scroll(self) -> None:
        """Реагирует на прокрутку: при достижении низа подгружает следующую страницу."""
        
        if self._loading:
            return
        sb = self._scroll.verticalScrollBar()
        if sb.maximum() <= 0:
            return
        if sb.value() >= int(sb.maximum() * 0.85):
            self._load_next_page()

    def _passes_view_filter(self, t: Task) -> bool:
        """Проверяет, подходит ли задача под текущий выбранный вид (фильтр)."""
        if self._active_view_key != "done" and t.done:
            return False
        if self._active_view_key == "done":
            return t.done
        if self._active_view_key == "all":
            return True
        if self._active_view_key == "important":
            return t.important
        if self._active_view_key == "deadlines":
            # Незавершённые: done уже отфильтрован выше. Дедлайн — просроченные или до конца ближайших 7 дней.
            if t.due is None:
                return False
            horizon = date.today() + timedelta(days=7)
            return t.due <= horizon
        if self._active_view_key.startswith("category:"):
            cid = self._active_view_key.split(":", 1)[1]
            return t.category_id == cid
        return True

    def _load_next_page(self) -> None:
        """Запускает асинхронную загрузку следующей страницы задач."""
        page_size = self._tasks_repo.page_size()
        if self._page_index * page_size >= len(self._view_tasks):
            return
        self._loading = True
        self._spinner.show()

        # simulate fetch delay so spinner is visible (and keeps UI smooth)
        QTimer.singleShot(250, self._finish_load_next_page)

    def _finish_load_next_page(self) -> None:
        """Вызывается таймером: фактически подгружает задачи и добавляет их в список."""
        page_size = self._tasks_repo.page_size()
        start = self._page_index * page_size
        end = start + page_size
        page = self._view_tasks[start:end]
        self._page_index += 1
        self._spinner.hide()
        self._empty_state.hide()

        for t in page:
            cat = next((c for c in self._categories if c.id == t.category_id), None)
            w = TaskItemWidget(self._paths, t, category=cat, parent=self._list_host)
            w.toggled_done.connect(self._on_task_done_toggled)
            w.menu_requested.connect(self._on_task_menu_requested)
            # Insert above the spinner (spinner should stay at the bottom).
            spinner_index = self._list_layout.indexOf(self._spinner)
            if spinner_index < 0:
                spinner_index = max(0, self._list_layout.count() - 1)
            self._list_layout.insertWidget(spinner_index, w)

        self._loading = False

    def _on_task_done_toggled(self, task_id: str, done: bool) -> None:
        """Сохраняет изменение чекбокса выполнения задачи в репозиторий."""
        self._tasks_repo.set_done(task_id, done)
        self._reset_and_load_first_page()

    def _on_task_menu_requested(self, task_id: str) -> None:
        """Открывает меню действий задачи (изменить/удалить)."""
        task = self._tasks_repo.get_by_id(task_id)
        if task is None:
            return

        menu = QMenu(self)
        toggle_done_action = menu.addAction("Отменить выполнение" if task.done else "Отметить выполненной")
        toggle_important_action = menu.addAction("Снять важность" if task.important else "Пометить важной")
        menu.addSeparator()
        edit_action = menu.addAction("Изменить")
        delete_action = menu.addAction("Удалить")
        chosen = menu.exec(QCursor.pos())
        if chosen == toggle_done_action:
            self._tasks_repo.set_done(task_id, not task.done)
            self._reset_and_load_first_page()
        elif chosen == toggle_important_action:
            self._tasks_repo.set_important(task_id, not task.important)
            self._reset_and_load_first_page()
        elif chosen == edit_action:
            self._edit_task(task_id)
        elif chosen == delete_action:
            self._delete_task(task_id)

    def _edit_task(self, task_id: str) -> None:
        """Открывает диалог редактирования задачи."""
        task = self._tasks_repo.get_by_id(task_id)
        if task is None:
            return
        dlg = CreateTaskDialog(self, categories=self._categories, task=task)
        if dlg.exec() != QDialog.Accepted:
            return
        title, cat_id, due, priority, important = dlg.result()
        if not title:
            return
        self._tasks_repo.update(
            task_id,
            title=title,
            category_id=cat_id,
            due=due,
            priority=priority,
            important=important,
        )
        self._reset_and_load_first_page()

    def _delete_task(self, task_id: str) -> None:
        """Удаляет задачу после подтверждения пользователем."""
        result = QMessageBox.question(
            self,
            "Удалить задачу",
            "Удалить выбранную задачу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        self._tasks_repo.delete(task_id)
        self._reset_and_load_first_page()

