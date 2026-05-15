from __future__ import annotations

"""Формирование QSS-стилей для отдельных элементов QLabel."""

from src.theme.theme import ThemeTokens, DerivedTokens


def labels_qss(tokens: ThemeTokens, der_tokens: DerivedTokens) -> str:
    return f""" 
            QFrame#TaskPriority {{ /* "Чипс" приоритета */
                border: 1px solid {tokens.border};
                border-radius: 4px;
                color: black;
            }}
            QLabel#TaskPriorityText {{
                color: black;
                font-weight: 800;
                background: transparent;
            }}
            
            QLabel#CategoryPillText {{ /* Текст внутри "Чипса" категории */
                color: {der_tokens.primary_bg};
                font-weight: 600;
                background: transparent;
            }}

            QFrame#TaskPriority[priority="1"] {{ /* Приоритет "низкий" */
            background: #C1E1C1;
            }}

            QFrame#TaskPriority[priority="2"] {{ /* Приоритет "Средний" */
                background: #B3D9FF;
            }}

            QFrame#TaskPriority[priority="3"] {{ /* Приоритет "Высокий" */
                background: #FFD1A1;
            }}

            QFrame#TaskPriority[priority="4"] {{ /* Приоритет "Критический" */
                background: #FFB3B3;
            }}

            QFrame#TaskImportant {{
                background: {tokens.surface_2};
                border: 1px solid {tokens.border};
                border-radius: 4px;
            }}
            QLabel#TaskImportantText {{
                color: {tokens.text};
                font-weight: 700;
                background: transparent;
            }}

            
            QLabel#CategoryIconLabel {{ /* "Чипс" с иконкой категории и кратким описанием */
                background: transparent;
                border: 1px solid {tokens.border};
                border-radius: 8px;
            }}

            QLabel#ViewTitleHeader {{ /* "Отображение названия категории" */
                font-size: 18px;
                font-weight: 900;
                color: {der_tokens.accent_text};
            }}

            QLabel#HeaderCategoryIcon {{
                background: transparent;
                border-radius: 7px;
            }}

            QLabel#TaskDue {{ /* Дедлайн */
                color: {tokens.text_muted};
            }}

            QLabel#SidebarSectionLabel {{ /* Подпись "Категории" перед фреймом категорий*/
                color: {tokens.text_muted};
                font-weight: 700;
                padding-top: 6px;
            }}

            QLabel#LoadingSpinner {{ /* Спиннер "Загружаем задачи" */
                color: {tokens.text_muted};
                opacity: 0.7;
                padding: 10px;
            }}

            QLabel#EmptyState {{ /* Отображается, когда не осталось задач */
                color: {tokens.text_muted};
                background: transparent;
                border: 1px dashed {tokens.border};
                border-radius: 12px;
                padding: 14px;
                font-weight: 700;
            }}

            
        """
