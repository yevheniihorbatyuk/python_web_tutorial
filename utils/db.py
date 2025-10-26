"""Утиліти для роботи з PostgreSQL, що використовуються в навчальних модулях."""
from __future__ import annotations

import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict, Iterable, List, Optional, Sequence

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class DatabaseConfig:
    """Описує параметри підключення до навчальної бази PostgreSQL."""

    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    database: str = os.getenv("POSTGRES_DB", "learning_db")
    user: str = os.getenv("POSTGRES_USER", "admin")
    password: str = os.getenv("POSTGRES_PASSWORD", "admin123")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
        }


def _resolve_config(config: Optional[DatabaseConfig] = None) -> DatabaseConfig:
    return config if config is not None else DatabaseConfig()


def get_connection(config: Optional[DatabaseConfig] = None) -> psycopg2.extensions.connection:
    """Створити нове підключення до БД згідно з конфігурацією."""

    cfg = _resolve_config(config)
    return psycopg2.connect(**cfg.as_dict())


@contextmanager
def get_db_connection(
    config: Optional[DatabaseConfig] = None,
) -> Iterable[psycopg2.extensions.connection]:
    """Context manager для автоматичного закриття з'єднання."""

    conn = get_connection(config)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor(
    config: Optional[DatabaseConfig] = None,
    *,
    dict_cursor: bool = False,
    commit: bool = True,
) -> Iterable[psycopg2.extensions.cursor]:
    """Надає курсор з автоматичним керуванням транзакцією."""

    with get_db_connection(config) as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        with conn.cursor(cursor_factory=cursor_factory) as cursor:
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception:
                conn.rollback()
                raise


def execute_query(
    query: str,
    params: Optional[Sequence[Any]] = None,
    *,
    fetch: str = "all",
    config: Optional[DatabaseConfig] = None,
    dict_cursor: bool = False,
):
    """Виконати SQL запит та повернути результати."""

    with get_cursor(config, dict_cursor=dict_cursor) as cursor:
        cursor.execute(query, params)

        if fetch == "all":
            return cursor.fetchall()
        if fetch == "one":
            return cursor.fetchone()
        return None


def execute_many(
    query: str,
    data: Sequence[Sequence[Any]],
    *,
    config: Optional[DatabaseConfig] = None,
) -> int:
    """Виконати запит для множинних даних."""

    with get_cursor(config) as cursor:
        cursor.executemany(query, data)
        return cursor.rowcount


def table_exists(table_name: str, *, config: Optional[DatabaseConfig] = None) -> bool:
    """Перевірити чи існує таблиця."""

    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = %s
        );
    """
    result = execute_query(query, (table_name,), fetch="one", config=config)
    return result[0] if result else False


def get_table_info(table_name: str, *, config: Optional[DatabaseConfig] = None) -> List[Dict[str, Any]]:
    """Отримати інформацію про колонки таблиці."""

    query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = %s
        ORDER BY ordinal_position;
    """
    rows = execute_query(query, (table_name,), config=config)

    return [
        {
            "column_name": row[0],
            "data_type": row[1],
            "is_nullable": row[2],
            "column_default": row[3],
        }
        for row in rows
    ] if rows else []


def get_database_stats(
    *,
    config: Optional[DatabaseConfig] = None,
    tables: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Отримати статистику бази даних."""

    stats: Dict[str, Any] = {}
    table_list = tables or [
        "departments",
        "employees",
        "customers",
        "categories",
        "products",
        "orders",
        "order_items",
    ]

    for table in table_list:
        if table_exists(table, config=config):
            query = f"SELECT COUNT(*) FROM {table};"
            result = execute_query(query, fetch="one", config=config)
            stats[table] = result[0] if result else 0

    return stats


class ConnectionPool:
    """Пул з'єднань для ефективної роботи з БД."""

    _pool: Optional[pool.SimpleConnectionPool] = None
    _config: DatabaseConfig = DatabaseConfig()

    @classmethod
    def initialize(
        cls,
        minconn: int = 1,
        maxconn: int = 10,
        *,
        config: Optional[DatabaseConfig] = None,
    ) -> None:
        if cls._pool is None:
            cls._config = _resolve_config(config)
            cls._pool = psycopg2.pool.SimpleConnectionPool(
                minconn,
                maxconn,
                **cls._config.as_dict(),
            )
            print(f"✅ Connection pool створено ({minconn}-{maxconn} з'єднань)")

    @classmethod
    @contextmanager
    def get_connection(cls) -> Iterable[psycopg2.extensions.connection]:
        if cls._pool is None:
            cls.initialize()

        conn = cls._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cls._pool.putconn(conn)

    @classmethod
    def close_all(cls) -> None:
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            print("✅ Connection pool закрито")


def test_connection(config: Optional[DatabaseConfig] = None) -> bool:
    """Тестувати підключення до БД."""

    try:
        with get_db_connection(config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print("✅ Підключення успішне!")
                print(f"PostgreSQL версія: {version[0]}")
                return True
    except Exception as exc:  # pragma: no cover - діагностика в навчальних цілях
        print(f"❌ Помилка підключення: {exc}")
        return False


def print_table_data(
    table_name: str,
    *,
    limit: int = 5,
    config: Optional[DatabaseConfig] = None,
) -> None:
    """Вивести дані з таблиці."""

    if not table_exists(table_name, config=config):
        print(f"❌ Таблиця {table_name} не існує")
        return

    query = f"SELECT * FROM {table_name} LIMIT %s;"
    rows = execute_query(query, (limit,), config=config)

    if rows:
        print(f"\n📊 Таблиця: {table_name}")
        print(f"Показано {len(rows)} рядків:")
        for row in rows:
            print(row)
    else:
        print(f"Таблиця {table_name} пуста")


def timing(func):
    """Декоратор для вимірювання часу виконання функції."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"⏱️  {func.__name__} виконано за {duration:.4f}с")
        return result

    return wrapper


__all__ = [
    "DatabaseConfig",
    "ConnectionPool",
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
