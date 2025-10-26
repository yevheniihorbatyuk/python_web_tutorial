"""
Модуль 6.1: Основи асинхронного програмування
===============================================

Цей модуль демонструє:
1. Різницю між синхронним та асинхронним кодом
2. Як працює Event Loop
3. async/await синтаксис
4. Практичні приклади з asyncio.sleep()
"""

import asyncio
import time
from colorama import Fore, Style, init

# Ініціалізація colorama для кольорового виводу
init(autoreset=True)


# ============================================
# 1. СИНХРОННИЙ КОД (Повільний)
# ============================================

def sync_task(name: str, duration: int):
    """Синхронна функція, яка блокує виконання"""
    print(f"{Fore.RED}[SYNC] Починаю {name}... (триватиме {duration}с)")
    time.sleep(duration)  # БЛОКУЄ весь код!
    print(f"{Fore.RED}[SYNC] Завершено {name}")
    return f"Результат {name}"


def run_sync_example():
    """Запустити синхронні задачі послідовно"""
    print(f"\n{Fore.YELLOW}{'=' * 60}")
    print(f"{Fore.YELLOW}СИНХРОННИЙ КОД - все виконується ПОСЛІДОВНО")
    print(f"{Fore.YELLOW}{'=' * 60}\n")

    start = time.time()

    # Кожна задача чекає завершення попередньої
    sync_task("Завдання 1", 2)
    sync_task("Завдання 2", 2)
    sync_task("Завдання 3", 2)

    duration = time.time() - start
    print(f"\n{Fore.RED}⏱️  Загальний час: {duration:.2f}с\n")


# ============================================
# 2. АСИНХРОННИЙ КОД (Швидкий!)
# ============================================

async def async_task(name: str, duration: int):
    """Асинхронна функція, яка НЕ блокує виконання"""
    print(f"{Fore.GREEN}[ASYNC] Починаю {name}... (триватиме {duration}с)")
    await asyncio.sleep(duration)  # Передає управління Event Loop
    print(f"{Fore.GREEN}[ASYNC] Завершено {name}")
    return f"Результат {name}"


async def run_async_example():
    """Запустити асинхронні задачі паралельно"""
    print(f"\n{Fore.YELLOW}{'=' * 60}")
    print(f"{Fore.YELLOW}АСИНХРОННИЙ КОД - все виконується ПАРАЛЕЛЬНО")
    print(f"{Fore.YELLOW}{'=' * 60}\n")

    start = time.time()

    # Всі задачі запускаються одночасно!
    await asyncio.gather(
        async_task("Завдання 1", 2),
        async_task("Завдання 2", 2),
        async_task("Завдання 3", 2),
    )

    duration = time.time() - start
    print(f"\n{Fore.GREEN}⏱️  Загальний час: {duration:.2f}с")
    print(f"{Fore.GREEN}🚀 Прискорення: ~3x швидше!\n")


# ============================================
# 3. ВІЗУАЛІЗАЦІЯ EVENT LOOP
# ============================================

async def visualize_event_loop():
    """Показати як Event Loop керує задачами"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}ВІЗУАЛІЗАЦІЯ EVENT LOOP")
    print(f"{Fore.CYAN}{'=' * 60}\n")

    async def task(name: str, delay: float):
        print(f"{Fore.CYAN}  → {name} запущено")
        await asyncio.sleep(delay)
        print(f"{Fore.CYAN}  ← {name} завершено через {delay}с")
        return name

    print(f"{Fore.WHITE}Event Loop запускає всі задачі:")
    print(f"{Fore.WHITE}  • Коли задача 'await', Loop переключається на іншу")
    print(f"{Fore.WHITE}  • Всі задачі виконуються 'паралельно'\n")

    start = time.time()

    # Запустити 5 задач з різними затримками
    tasks = [
        task("Task A", 1.0),
        task("Task B", 0.5),
        task("Task C", 1.5),
        task("Task D", 0.3),
        task("Task E", 1.0),
    ]

    results = await asyncio.gather(*tasks)

    duration = time.time() - start
    print(f"\n{Fore.CYAN}✅ Всі задачі завершені за {duration:.2f}с")
    print(f"{Fore.CYAN}📊 Результати: {results}\n")


# ============================================
# 4. ПРАКТИЧНИЙ ПРИКЛАД: Завантаження даних
# ============================================

async def fetch_user_data(user_id: int) -> dict:
    """Імітація завантаження даних користувача з API"""
    print(f"{Fore.MAGENTA}📥 Завантаження даних користувача {user_id}...")
    await asyncio.sleep(0.5)  # Імітація мережевого запиту
    return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}


async def fetch_user_orders(user_id: int) -> list:
    """Імітація завантаження замовлень користувача"""
    print(f"{Fore.MAGENTA}📦 Завантаження замовлень користувача {user_id}...")
    await asyncio.sleep(0.7)  # Імітація мережевого запиту
    return [{"id": i, "product": f"Product {i}"} for i in range(1, 4)]


async def fetch_user_profile(user_id: int) -> dict:
    """Завантажити повний профіль користувача"""
    print(f"\n{Fore.MAGENTA}🔄 Завантаження профілю користувача {user_id}...")

    start = time.time()

    # Паралельне завантаження даних та замовлень
    user_data, orders = await asyncio.gather(
        fetch_user_data(user_id),
        fetch_user_orders(user_id)
    )

    duration = time.time() - start

    profile = {
        **user_data,
        "orders": orders,
        "total_orders": len(orders)
    }

    print(f"{Fore.MAGENTA}✅ Профіль завантажено за {duration:.2f}с")
    return profile


async def practical_example():
    """Практичний приклад: завантаження даних кількох користувачів"""
    print(f"\n{Fore.YELLOW}{'=' * 60}")
    print(f"{Fore.YELLOW}ПРАКТИЧНИЙ ПРИКЛАД: Завантаження профілів")
    print(f"{Fore.YELLOW}{'=' * 60}\n")

    start = time.time()

    # Завантажити профілі 3 користувачів паралельно
    profiles = await asyncio.gather(
        fetch_user_profile(1),
        fetch_user_profile(2),
        fetch_user_profile(3),
    )

    duration = time.time() - start

    print(f"\n{Fore.GREEN}{'=' * 60}")
    print(f"{Fore.GREEN}📊 Результати:")
    for profile in profiles:
        print(f"{Fore.GREEN}  • {profile['name']}: {profile['total_orders']} замовлень")
    print(f"{Fore.GREEN}⏱️  Загальний час: {duration:.2f}с")
    print(f"{Fore.GREEN}{'=' * 60}\n")


# ============================================
# 5. ОБРОБКА ПОМИЛОК
# ============================================

async def task_with_error(name: str, should_fail: bool = False):
    """Задача, яка може завершитись з помилкою"""
    print(f"{Fore.BLUE}[{name}] Починаю...")
    await asyncio.sleep(1)

    if should_fail:
        print(f"{Fore.RED}[{name}] ❌ Помилка!")
        raise ValueError(f"Помилка в {name}")

    print(f"{Fore.BLUE}[{name}] ✅ Успішно!")
    return f"Результат {name}"


async def error_handling_example():
    """Демонстрація обробки помилок в async коді"""
    print(f"\n{Fore.YELLOW}{'=' * 60}")
    print(f"{Fore.YELLOW}ОБРОБКА ПОМИЛОК")
    print(f"{Fore.YELLOW}{'=' * 60}\n")

    try:
        results = await asyncio.gather(
            task_with_error("Task 1", False),
            task_with_error("Task 2", True),  # Ця задача впаде
            task_with_error("Task 3", False),
            return_exceptions=True  # Не зупиняти всі задачі при помилці
        )

        print(f"\n{Fore.BLUE}Результати:")
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"{Fore.RED}  Task {i}: Помилка - {result}")
            else:
                print(f"{Fore.GREEN}  Task {i}: {result}")

    except Exception as e:
        print(f"{Fore.RED}Критична помилка: {e}")


# ============================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================

async def main():
    """Запустити всі демонстрації"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}  МОДУЛЬ 6.1: АСИНХРОННЕ ПРОГРАМУВАННЯ В PYTHON")
    print(f"{Fore.CYAN}{'=' * 60}\n")

    # 1. Порівняння sync vs async
    run_sync_example()
    await run_async_example()

    # 2. Візуалізація Event Loop
    await visualize_event_loop()

    # 3. Практичний приклад
    await practical_example()

    # 4. Обробка помилок
    await error_handling_example()

    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.GREEN}✅ Всі приклади завершено!")
    print(f"{Fore.CYAN}{'=' * 60}\n")

    # Підсумок
    print(f"{Fore.YELLOW}📚 Ключові висновки:")
    print(f"{Fore.WHITE}  1. Синхронний код: послідовне виконання (повільно)")
    print(f"{Fore.WHITE}  2. Асинхронний код: паралельне виконання (швидко)")
    print(f"{Fore.WHITE}  3. Event Loop: керує виконанням async задач")
    print(f"{Fore.WHITE}  4. await: передає управління Event Loop")
    print(f"{Fore.WHITE}  5. asyncio.gather(): запускає кілька задач паралельно\n")


if __name__ == "__main__":
    # Запустити головну async функцію
    asyncio.run(main())
