from __future__ import annotations

"""Формирование QSS-стилей для отдельных элементов QLabel."""

from dataclasses import dataclass

from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from src.core.models import Settings
from src.theme.theme import ThemeTokens, DerivedTokens


def labels_qss(tokens: ThemeTokens, der_tokens: DerivedTokens) -> str:
    return (
        f""" 
            QLabel#TaskPriority {{ /* "Чипс" приоритета */
                border: 1px solid {tokens.border};
                border-radius: 8px;
                color: black;
            }}

            QLabel#TaskPriority[priority="1"] {{ /* Приоритет "низкий" */
            background: #C1E1C1;
            }}

            QLabel#TaskPriority[priority="2"] {{ /* Приоритет "Средний" */
                background: #B3D9FF;
            }}

            QLabel#TaskPriority[priority="3"] {{ /* Приоритет "Высокий" */
                background: #FFD1A1;
            }}

            QLabel#TaskPriority[priority="4"] {{ /* Приоритет "Критический" */
                background: #FFB3B3;
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
    )