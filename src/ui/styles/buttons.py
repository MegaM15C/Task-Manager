from __future__ import annotations

"""Формирование QSS-стилей для отдельных элементов Кнопок."""

from dataclasses import dataclass

from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from src.core.models import Settings
from src.theme.theme import ThemeTokens, DerivedTokens


def buttons_qss(tokens: ThemeTokens, der_tokens: DerivedTokens) -> str:
    return f"""
        QPushButton {{ /* Все кнопки */
            background: {tokens.surface_2};
            border: 1px solid {tokens.border};
            border-radius: 10px;
            padding: 8px 12px;
        }}
        QPushButton:hover {{
            background: {tokens.surface};
        }}
        QPushButton#NavButton {{ /* Все кнопки */
            background: {tokens.surface_2};
            border: 1px solid {tokens.border};
            border-radius: 10px;
            padding: 8px 8px;
            text-align: left;
            font-size: 16px;
            font-weight: 700;
        }}
        QPushButton#NavButton:hover {{
            background: {tokens.surface};
        }}
        QPushButton#PrimaryButton {{ /* Кнопка добавления задачи */
            background: {tokens.accent};
            border: 0.6px solid {tokens.border};
            border-radius: 8px;
            color: {der_tokens.accent_text};
            font-weight: 800;
        }}
        QPushButton#PrimaryButton:hover {{
            border: 0.6px solid {tokens.border};
            border-radius: 8px;
            color: {der_tokens.accent_text};
            font-weight: 800;
        }}
        
        QPushButton#AcceptButton {{ /* Кнопка подтверждения настроек, категории, задачи */
            background: {der_tokens.primary_bg}; 
            border: 0.6px solid {tokens.border};
            border-radius: 8px;
            color: {der_tokens.primary_text};
            font-weight: 800;
        }}
        QPushButton#AcceptButton:hover {{
            background: {tokens.accent};
            border: 0.6px solid {tokens.border};
            border-radius: 8px;
            color: {der_tokens.primary_text};
            font-weight: 800;
        }}
        
        QPushButton#AccentPreview {{ /* Кнопка "круга" в категории и настройках */
            border: 2px solid {tokens.border};
            border-radius: 14px;
        }}
        """


def tool_buttons_qss(tokens: ThemeTokens) -> str:
    return f"""
        QToolButton#PinButton:hover, QToolButton#ThemeButton:hover, QToolButton#SettingsButton:hover {{
            background-color: rgba(0, 0, 0, 30);  /* слегка темнеет */
            border-radius: 8px;
        }}
        QToolButton#PinButton, QToolButton#ThemeButton, QToolButton#SettingsButton {{
            background: {tokens.surface_2};
            border: 1px solid {tokens.border};
            border-radius: 10px;
        }}
        """
