"""Допоміжні утиліти для роботи з базою даних."""
from __future__ import annotations

from functools import wraps
from typing import Any, Dict

from .db import (
    ConnectionPool,
    DatabaseConfig,
    execute_many,
    execute_query,
    get_connection,
    get_cursor,
    get_database_stats,
    get_db_connection,
    get_table_info,
    print_table_data,
    table_exists,
    test_connection,
    timing,
)

__all__ = [
    "ConnectionPool",
    "DatabaseConfig",
    "execute_many",
    "execute_query",
    "get_connection",
    "get_cursor",
    "get_database_stats",
    "get_db_connection",
    "get_table_info",
    "print_table_data",
    "table_exists",
    "test_connection",
    "timing",
]


# Зворотна сумісність: прості псевдоніми для викликів у старих модулях
DB_CONFIG: Dict[str, Any] = DatabaseConfig().as_dict()


def with_connection(func):
    """Декоратор для автоматичної передачі підключення."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_db_connection() as conn:
            return func(conn, *args, **kwargs)

    return wrapper


# Перелік імен, що залишаються для сумісності (наприклад, у навчальних матеріалах)
__all__ += ["DB_CONFIG", "with_connection"]
