from __future__ import annotations

"""Формирование QSS-стилей для отдельных 
элементов управления"""

from dataclasses import dataclass

from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from src.core.models import Settings
from src.theme.theme import ThemeTokens, DerivedTokens


def controls_qss(tokens: ThemeTokens, der_tokens: DerivedTokens) -> str:
    return (
        f"""
        QCheckBox#ImportantCheckBox {{
            background: transparent;
            border: 1px solid {tokens.border};
            border-radius: 10px;
            padding: 8px 10px;
        }}
        QCheckBox#ImportantCheckBox::indicator {{
            background: transparent;
            border: 1px solid {tokens.border};
            border-radius: 4px;  /* ← скругление */
            width: 16px;
            height: 16px;
        }}
        QCheckBox#ImportantCheckBox::indicator:checked {{
            background: {der_tokens.primary_bg};
            border: 1px solid {tokens.border};
            image: url(resources/icons/check.png);
            border-radius: 4px;
        }}

        QCheckBox#TaskCheckBox::indicator {{
            background: transparent;
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid {tokens.border};
        }}
        QCheckBox#TaskCheckBox::indicator:checked {{
            width: 16px;
            height: 16px;
            background-color: {der_tokens.primary_bg};
            border: 1px solid {tokens.border};
            border-radius: 4px;
            image: url(resources/icons/check.png); 
        }}

        QLineEdit, QComboBox, QDateEdit {{
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: 10px;
            padding: 8px 10px;
            selection-background-color: {tokens.accent};
        }}
        QComboBox::drop-down {{
            border: 0px;
            width: 26px;
        }}

        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 1px;
        }}
        QScrollBar::handle:vertical {{
            background: {tokens.border};
            border-radius: 2px;
            min-height: 30px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}


        """
    )