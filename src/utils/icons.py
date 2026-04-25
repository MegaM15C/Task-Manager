from pathlib import Path

icons_dir = Path("./resources/icons")
sidebar_dir = Path("./resources/icons/sidebar")
task_icons_dir = Path("./resources/icons/task-icons")

icons = {
    # Иконки сайдбара
    "collapse_sidebar": sidebar_dir / "collapse.png",
    "expand_sidebar": sidebar_dir / "expand.png",
    "dark_theme_indicator": sidebar_dir / "dark_theme_indicator.png",
    "light_theme_indicator": sidebar_dir / "light_theme_indicator.png",
    "settings": sidebar_dir / "settings.png",
    # Иконки категорий задач
    "all_tasks": task_icons_dir / "all_tasks.png",
    "completed_tasks": task_icons_dir / "completed_tasks.png",
    "deadlines": task_icons_dir / "deadline.png",
    "important": task_icons_dir / "important.png",
    # Прочие иконки
    "check": icons_dir / "check.png",
    "important_mask": icons_dir / "important_mask.png",
}
