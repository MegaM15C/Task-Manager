from __future__ import annotations

"""Формирование QSS-стилей для отдельных больших элементов, будь то HEADER и др"""

from dataclasses import dataclass

from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from src.core.models import Settings
from src.theme.theme import ThemeTokens, DerivedTokens


def components_qss(tokens: ThemeTokens, der_tokens: DerivedTokens) -> str:
    return (
        f"""
        QFrame#MainArea {{ /* Главное окно (ROOT) */
            border: 1px solid {tokens.border};
            border-radius: 14px;
        }}

        QWidget#Header {{ /* Верхняя часть у главного экрана (HEADER)  */
            background-color: {der_tokens.primary_bg};
            border-radius: 12px;
            border: 1px solid {tokens.border};
        }}

        QFrame#TaskItem {{ /* Элемент "Задача" 1 строка (task 1 row) */
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: 14px;
        }}

        QFrame#Sidebar {{ /* Сайдбар (Sidebar) */
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: 12px;
        }}

        QWidget#Overlay {{ /* Диалоговые окна */
            background: rgba(10, 10, 10, 140);
        }}
        
        QFrame#DialogCard {{
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: 8px;
        }}

        QMenu {{ /* Выпадающее меню */
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: 10px;
            padding: 6px;
        }}
        QMenu::item {{ /* Элемент выпадающего меню */
            background: transparent;
            border-radius: 8px;
            padding: 8px 12px;
        }}
        QMenu::item:selected {{
            background: {tokens.surface_2};
            border-radius: 8px;
            padding: 8px 12px;
        }}
        
        """
    )