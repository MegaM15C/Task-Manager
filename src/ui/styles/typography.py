from __future__ import annotations

"""Базовые QSS-стили типографии для всего приложения."""

from dataclasses import dataclass

from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from src.core.models import Settings
from src.theme.theme import ThemeTokens


def typography_qss(tokens: ThemeTokens) -> str:
    return (
        f"""
            QLabel {{
                background: transparent;
            }}
        """
    )