from src.utils.resources import resource_path


def _p(relative: str) -> str:
    """Возвращает абсолютный POSIX-путь к файлу иконки."""
    return resource_path(relative).as_posix()


icons = {
    # Иконки сайдбара
    "collapse_sidebar": _p("resources/icons/sidebar/collapse.png"),
    "expand_sidebar": _p("resources/icons/sidebar/expand.png"),
    "dark_theme_indicator": _p("resources/icons/sidebar/dark_theme_indicator.png"),
    "light_theme_indicator": _p("resources/icons/sidebar/light_theme_indicator.png"),
    "settings": _p("resources/icons/sidebar/settings.png"),
    # Иконки категорий задач
    "all_tasks": _p("resources/icons/task-icons/all_tasks.png"),
    "completed_tasks": _p("resources/icons/task-icons/completed_tasks.png"),
    "deadlines": _p("resources/icons/task-icons/deadline.png"),
    "important": _p("resources/icons/task-icons/important.png"),
    # Прочие иконки
    "check": _p("resources/icons/check.png"),
    "important_mask": _p("resources/icons/important_mask.png"),
    "arrow_down": _p("resources/icons/arrow_down.png"),
}
