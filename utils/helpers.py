"""
Допоміжні утиліти для роботи з базою даних
"""

import os
import time
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import Optional, Dict, List, Any
from functools import wraps
from dotenv import load_dotenv

# Завантажити змінні середовища з .env файлу
load_dotenv()


# ============================================
# Конфігурація підключення до БД
# ============================================

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'learning_db'),
    'user': os.getenv('POSTGRES_USER', 'admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'admin123')
}


# ============================================
# Функції для роботи з підключенням
# ============================================

def get_connection():
    """Створити нове підключення до БД"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Помилка підключення до БД: {e}")
        raise


@contextmanager
def get_db_connection():
    """Context manager для автоматичного закриття з'єднання"""
    conn = None
    try:
        conn = get_connection()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


@contextmanager
def get_cursor(commit=True):
    """Context manager для роботи з курсором"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


# ============================================
# Виконання запитів
# ============================================

def execute_query(query: str, params: tuple = None, fetch: str = 'all') -> Optional[List]:
    """
    Виконати SQL запит та повернути результати

    Args:
        query: SQL запит
        params: Параметри для запиту
        fetch: 'all', 'one', або 'none'

    Returns:
        Результати запиту або None
    """
    with get_cursor() as cursor:
        cursor.execute(query, params)

        if fetch == 'all':
            return cursor.fetchall()
        elif fetch == 'one':
            return cursor.fetchone()
        else:
            return None


def execute_many(query: str, data: List[tuple]) -> int:
    """
    Виконати запит для множинних даних

    Args:
        query: SQL запит
        data: Список кортежів з даними

    Returns:
        Кількість оброблених рядків
    """
    with get_cursor() as cursor:
        cursor.executemany(query, data)
        return cursor.rowcount


# ============================================
# Перевірки та утиліти
# ============================================

def table_exists(table_name: str) -> bool:
    """Перевірити чи існує таблиця"""
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = %s
        );
    """
    result = execute_query(query, (table_name,), fetch='one')
    return result[0] if result else False


def get_table_info(table_name: str) -> List[Dict]:
    """Отримати інформацію про колонки таблиці"""
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
    rows = execute_query(query, (table_name,))

    return [
        {
            'column_name': row[0],
            'data_type': row[1],
            'is_nullable': row[2],
            'column_default': row[3]
        }
        for row in rows
    ] if rows else []


def get_database_stats() -> Dict[str, Any]:
    """Отримати статистику бази даних"""
    stats = {}

    # Кількість записів у кожній таблиці
    tables = ['departments', 'employees', 'customers', 'categories',
              'products', 'orders', 'order_items']

    for table in tables:
        if table_exists(table):
            query = f"SELECT COUNT(*) FROM {table};"
            result = execute_query(query, fetch='one')
            stats[table] = result[0] if result else 0

    return stats


# ============================================
# Декоратори
# ============================================

def timing(func):
    """Декоратор для вимірювання часу виконання функції"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"⏱️  {func.__name__} виконано за {duration:.4f}с")
        return result
    return wrapper


def with_connection(func):
    """Декоратор для автоматичної передачі підключення"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_db_connection() as conn:
            return func(conn, *args, **kwargs)
    return wrapper


# ============================================
# Connection Pool (для продакшн)
# ============================================

class ConnectionPool:
    """Пул з'єднань для ефективної роботи з БД"""

    _pool = None

    @classmethod
    def initialize(cls, minconn=1, maxconn=10):
        """Ініціалізувати пул з'єднань"""
        if cls._pool is None:
            cls._pool = psycopg2.pool.SimpleConnectionPool(
                minconn,
                maxconn,
                **DB_CONFIG
            )
            print(f"✅ Connection pool створено ({minconn}-{maxconn} з'єднань)")

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Отримати з'єднання з пулу"""
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
    def close_all(cls):
        """Закрити всі з'єднання"""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            print("✅ Connection pool закрито")


# ============================================
# Допоміжні функції для тестування
# ============================================

def test_connection() -> bool:
    """Тестувати підключення до БД"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✅ Підключення успішне!")
                print(f"PostgreSQL версія: {version[0]}")
                return True
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")
        return False


def print_table_data(table_name: str, limit: int = 5):
    """Вивести дані з таблиці"""
    if not table_exists(table_name):
        print(f"❌ Таблиця {table_name} не існує")
        return

    query = f"SELECT * FROM {table_name} LIMIT %s;"
    rows = execute_query(query, (limit,))

    if rows:
        print(f"\n📊 Таблиця: {table_name}")
        print(f"Показано {len(rows)} рядків:")
        for row in rows:
            print(row)
    else:
        print(f"Таблиця {table_name} пуста")


if __name__ == "__main__":
    # Тестування модуля
    print("=" * 60)
    print("Тестування helpers.py")
    print("=" * 60)

    # Тест підключення
    test_connection()

    # Статистика БД
    print("\n📊 Статистика бази даних:")
    stats = get_database_stats()
    for table, count in stats.items():
        print(f"  {table}: {count} записів")

    # Тест пулу з'єднань
    print("\n🔄 Тест connection pool:")
    ConnectionPool.initialize(minconn=2, maxconn=5)

    with ConnectionPool.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM customers;")
            count = cursor.fetchone()[0]
            print(f"  Клієнтів у БД: {count}")

    ConnectionPool.close_all()

    print("\n✅ Всі тести пройдено!")
