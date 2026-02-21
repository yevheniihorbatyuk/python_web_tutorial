"""
Модуль 6.5: Робота з PostgreSQL через Python
============================================

Цей модуль демонструє:
1. Підключення до PostgreSQL з Python
2. CRUD операції
3. SQL Injection захист
4. Транзакції
5. Batch операції
"""

import sys
import os

# Додати шлях до utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2.extras import RealDictCursor
from colorama import Fore, init
from utils.helpers import get_db_connection, execute_query, timing

init(autoreset=True)


# ============================================
# 1. БАЗОВЕ ПІДКЛЮЧЕННЯ
# ============================================

def demo_basic_connection():
    """Демонстрація базового підключення"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}1. БАЗОВЕ ПІДКЛЮЧЕННЯ ДО POSTGRESQL")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    try:
        # ⚠️  ТІЛЬКИ ДЛЯ ДЕМОНСТРАЦІЇ raw-підключення!
        # У реальному проекті: utils/helpers.py читає credentials з .env файлу
        # Причина: git history зберігає credentials назавжди навіть після їх видалення
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="learning_db",
            user="admin",
            password="admin123"
        )

        print(f"{Fore.GREEN}✅ Підключення успішне!")

        # Створити курсор
        cursor = conn.cursor()

        # Виконати простий запит
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"{Fore.CYAN}PostgreSQL версія: {version[0][:50]}...")

        # Закрити
        cursor.close()
        conn.close()
        print(f"{Fore.GREEN}✅ З'єднання закрито\n")

    except Exception as e:
        print(f"{Fore.RED}❌ Помилка: {e}\n")


# ============================================
# 2. CONTEXT MANAGER
# ============================================

def demo_context_manager():
    """Демонстрація використання context manager"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}2. CONTEXT MANAGER (Автоматичне закриття)")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    # Використання context manager - автоматично закриває з'єднання
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM customers;")
            count = cursor.fetchone()[0]
            print(f"{Fore.GREEN}Клієнтів у БД: {count}")

    print(f"{Fore.GREEN}✅ З'єднання автоматично закрито\n")


# ============================================
# 3. CRUD ОПЕРАЦІЇ
# ============================================

def demo_create():
    """CREATE - Додати нового клієнта"""
    print(f"\n{Fore.YELLOW}3.1 CREATE - Додати запис")

    query = """
        INSERT INTO customers (first_name, last_name, email, phone, city)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, first_name, last_name;
    """

    params = ("Тест", "Тестович", "test@example.com", "+380991234567", "Kyiv")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                print(f"{Fore.GREEN}✅ Додано клієнта: ID={result[0]}, Ім'я={result[1]} {result[2]}")
                return result[0]
    except psycopg2.IntegrityError:
        print(f"{Fore.YELLOW}⚠️  Клієнт з таким email вже існує")
        return None


def demo_read():
    """READ - Прочитати дані"""
    print(f"\n{Fore.YELLOW}3.2 READ - Прочитати записи")

    query = "SELECT id, first_name, last_name, email, city FROM customers LIMIT 5;"

    rows = execute_query(query)

    print(f"{Fore.CYAN}Перші 5 клієнтів:")
    for row in rows:
        print(f"{Fore.WHITE}  ID: {row[0]}, Ім'я: {row[1]} {row[2]}, Email: {row[3]}, Місто: {row[4]}")


def demo_update(customer_id: int):
    """UPDATE - Оновити дані"""
    print(f"\n{Fore.YELLOW}3.3 UPDATE - Оновити запис")

    query = """
        UPDATE customers
        SET city = %s
        WHERE id = %s
        RETURNING first_name, last_name, city;
    """

    params = ("Lviv", customer_id)

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                print(f"{Fore.GREEN}✅ Оновлено: {result[0]} {result[1]}, нове місто: {result[2]}")
            else:
                print(f"{Fore.RED}❌ Клієнта з ID {customer_id} не знайдено")


def demo_delete(customer_id: int):
    """DELETE - Видалити дані"""
    print(f"\n{Fore.YELLOW}3.4 DELETE - Видалити запис")

    query = "DELETE FROM customers WHERE id = %s RETURNING first_name, last_name;"

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (customer_id,))
            result = cursor.fetchone()
            if result:
                print(f"{Fore.GREEN}✅ Видалено: {result[0]} {result[1]}")
            else:
                print(f"{Fore.RED}❌ Клієнта з ID {customer_id} не знайдено")


# ============================================
# 4. SQL INJECTION ЗАХИСТ
# ============================================

def demo_sql_injection():
    """Демонстрація захисту від SQL injection"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}4. SQL INJECTION ЗАХИСТ")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    # ❌ НЕБЕЗПЕЧНО - НЕ РОБІТЬ ТАК!
    user_input = '{user_input}'
    print(f"{Fore.RED}❌ НЕБЕЗПЕЧНИЙ КОД (НЕ використовувати):")
    print(f"{Fore.YELLOW}query = f\"SELECT * FROM users WHERE email = '{user_input}'\"")
    print(f"{Fore.RED}Це дозволяє SQL injection атаки!\n")

    # ✅ БЕЗПЕЧНО - Використовуйте параметризовані запити
    print(f"{Fore.GREEN}✅ БЕЗПЕЧНИЙ КОД:")
    print(f"{Fore.YELLOW}query = \"SELECT * FROM users WHERE email = %s\"")
    print(f"{Fore.YELLOW}cursor.execute(query, (user_input,))")

    # Демонстрація
    email = "test@example.com"
    query = "SELECT first_name, last_name, email FROM customers WHERE email = %s;"

    rows = execute_query(query, (email,))

    if rows:
        print(f"{Fore.GREEN}\nЗнайдено {len(rows)} клієнтів з email {email}")
        for row in rows:
            print(f"{Fore.WHITE}  {row[0]} {row[1]} - {row[2]}")
    else:
        print(f"{Fore.YELLOW}\nКлієнтів з email {email} не знайдено")


# ============================================
# 5. СКЛАДНІ ЗАПИТИ
# ============================================

def demo_complex_queries():
    """Складні запити з JOIN"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}5. СКЛАДНІ ЗАПИТИ З JOIN")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    query = """
        SELECT
            c.first_name || ' ' || c.last_name AS customer_name,
            COUNT(o.id) AS order_count,
            COALESCE(SUM(o.total_amount), 0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.first_name, c.last_name
        HAVING COUNT(o.id) > 0
        ORDER BY total_spent DESC
        LIMIT 5;
    """

    # Використання RealDictCursor для отримання словників
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

            print(f"{Fore.CYAN}Топ-5 клієнтів за сумою покупок:")
            for row in rows:
                print(f"{Fore.WHITE}  {row['customer_name']:20} | "
                      f"Замовлень: {row['order_count']:2} | "
                      f"Сума: {row['total_spent']:10.2f} грн")


# ============================================
# 6. BATCH ОПЕРАЦІЇ
# ============================================

def demo_batch_operations():
    """Batch операції - вставка багатьох записів"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}6. BATCH ОПЕРАЦІЇ")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    # Підготувати дані
    products_data = [
        ("Test Product 1", 2, 999.99, 10),
        ("Test Product 2", 2, 1299.99, 5),
        ("Test Product 3", 3, 799.99, 15),
    ]

    query = """
        INSERT INTO products (name, category_id, price, stock_quantity)
        VALUES (%s, %s, %s, %s);
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, products_data)
                print(f"{Fore.GREEN}✅ Додано {cursor.rowcount} товарів")

                # Видалити тестові товари
                cursor.execute("DELETE FROM products WHERE name LIKE 'Test Product%';")
                print(f"{Fore.YELLOW}🧹 Видалено {cursor.rowcount} тестових товарів")

    except Exception as e:
        print(f"{Fore.RED}❌ Помилка: {e}")


# ============================================
# 7. ТРАНЗАКЦІЇ
# ============================================

def demo_transactions():
    """Демонстрація транзакцій"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}7. ТРАНЗАКЦІЇ")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    print(f"{Fore.YELLOW}Симуляція переказу грошей між рахунками:")
    print(f"{Fore.WHITE}  1. Зняти гроші з рахунку A")
    print(f"{Fore.WHITE}  2. Додати гроші на рахунок B")
    print(f"{Fore.WHITE}  3. Якщо помилка - відкатити обидві операції\n")

    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="learning_db",
            user="admin",
            password="admin123"
        )

        cursor = conn.cursor()

        # Початок транзакції (автоматично)
        print(f"{Fore.CYAN}Початок транзакції...")

        # Операція 1
        cursor.execute("UPDATE products SET price = price - 100 WHERE id = 1;")
        print(f"{Fore.GREEN}✓ Операція 1 виконана")

        # Операція 2
        cursor.execute("UPDATE products SET price = price + 100 WHERE id = 2;")
        print(f"{Fore.GREEN}✓ Операція 2 виконана")

        # Commit - застосувати зміни
        conn.commit()
        print(f"{Fore.GREEN}✅ Транзакція успішно завершена (COMMIT)\n")

        # Відкат змін для демонстрації
        cursor.execute("UPDATE products SET price = price + 100 WHERE id = 1;")
        cursor.execute("UPDATE products SET price = price - 100 WHERE id = 2;")
        conn.commit()
        print(f"{Fore.YELLOW}🔄 Зміни відкачено для демонстрації")

        cursor.close()

    except Exception as e:
        if conn:
            conn.rollback()
            print(f"{Fore.RED}❌ Помилка! Транзакція відкачена (ROLLBACK)")
            print(f"{Fore.RED}Помилка: {e}")

    finally:
        if conn:
            conn.close()


# ============================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================

def main():
    """Запустити всі демонстрації"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}  МОДУЛЬ 6.5: РОБОТА З POSTGRESQL ЧЕРЕЗ PYTHON")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    # 1. Базове підключення
    demo_basic_connection()

    # 2. Context Manager
    demo_context_manager()

    # 3. CRUD операції
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}3. CRUD ОПЕРАЦІЇ")
    print(f"{Fore.CYAN}{'=' * 70}")

    customer_id = demo_create()
    demo_read()
    if customer_id:
        demo_update(customer_id)
        demo_delete(customer_id)

    # 4. SQL Injection
    demo_sql_injection()

    # 5. Складні запити
    demo_complex_queries()

    # 6. Batch операції
    demo_batch_operations()

    # 7. Транзакції
    demo_transactions()

    # Підсумок
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.GREEN}✅ Всі демонстрації завершено!")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    print(f"{Fore.YELLOW}📚 Ключові висновки:")
    print(f"{Fore.WHITE}  1. Використовуйте context managers для автоматичного закриття")
    print(f"{Fore.WHITE}  2. ЗАВЖДИ використовуйте параметризовані запити (%s)")
    print(f"{Fore.WHITE}  3. Для множинних INSERT використовуйте executemany()")
    print(f"{Fore.WHITE}  4. Транзакції: COMMIT для збереження, ROLLBACK для відкату")
    print(f"{Fore.WHITE}  5. RealDictCursor для отримання результатів як словників\n")


if __name__ == "__main__":
    main()
