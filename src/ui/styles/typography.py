from __future__ import annotations

"""Базовые QSS-стили типографии для всего приложения."""

from src.theme.theme import ThemeTokens


def typography_qss(tokens: ThemeTokens) -> str:
    return f"""
            QLabel {{
                background: transparent;
                font-weight: 400;
            }}
        """
