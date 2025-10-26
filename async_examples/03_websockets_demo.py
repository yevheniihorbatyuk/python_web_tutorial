"""
Модуль 6.3: WebSockets з aiohttp (Опціонально)
===============================================

Цей модуль демонструє:
1. Що таке WebSockets і коли їх використовувати
2. Створення WebSocket сервера
3. Створення WebSocket клієнта
4. Порівняння HTTP vs WebSockets
"""

import asyncio
import aiohttp
from aiohttp import web
from colorama import Fore, init
from datetime import datetime

# Ініціалізація colorama
init(autoreset=True)


# ============================================
# WEBSOCKET СЕРВЕР
# ============================================

# Зберігання активних з'єднань
active_connections = set()


async def websocket_handler(request):
    """Обробник WebSocket з'єднань"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Додати нове з'єднання
    active_connections.add(ws)
    print(f"{Fore.GREEN}[SERVER] Нове з'єднання. Всього: {len(active_connections)}")

    try:
        # Привітання
        await ws.send_str(f"Привіт! Ти підключився до WebSocket сервера о {datetime.now().strftime('%H:%M:%S')}")

        # Слухати повідомлення від клієнта
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(f"{Fore.CYAN}[SERVER] Отримано: {msg.data}")

                # Відправити відповідь клієнту
                response = f"Echo: {msg.data}"
                await ws.send_str(response)

                # Broadcast повідомлення всім клієнтам
                for connection in active_connections:
                    if connection != ws:
                        await connection.send_str(f"[Broadcast] {msg.data}")

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"{Fore.RED}[SERVER] Помилка: {ws.exception()}")

    finally:
        # Видалити з'єднання
        active_connections.discard(ws)
        print(f"{Fore.YELLOW}[SERVER] З'єднання закрито. Залишилось: {len(active_connections)}")

    return ws


async def http_handler(request):
    """Звичайний HTTP обробник для порівняння"""
    return web.Response(text="Це HTTP відповідь. Спробуй /ws для WebSocket!")


async def start_server():
    """Запустити WebSocket сервер"""
    app = web.Application()
    app.router.add_get('/', http_handler)
    app.router.add_get('/ws', websocket_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    print(f"{Fore.GREEN}{'=' * 70}")
    print(f"{Fore.GREEN}WebSocket сервер запущено на http://localhost:8080/ws")
    print(f"{Fore.GREEN}{'=' * 70}\n")

    return runner


# ============================================
# WEBSOCKET КЛІЄНТ
# ============================================

async def websocket_client(client_id: int, messages: list):
    """WebSocket клієнт"""
    uri = 'http://localhost:8080/ws'

    print(f"{Fore.CYAN}[CLIENT {client_id}] Підключення до {uri}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(uri) as ws:
                print(f"{Fore.GREEN}[CLIENT {client_id}] Підключено!")

                # Слухати повідомлення у фоні
                async def receive_messages():
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            print(f"{Fore.MAGENTA}[CLIENT {client_id}] ← {msg.data}")
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print(f"{Fore.RED}[CLIENT {client_id}] Помилка")
                            break

                # Створити задачу для отримання повідомлень
                receive_task = asyncio.create_task(receive_messages())

                # Відправити повідомлення
                for message in messages:
                    await asyncio.sleep(1)  # Пауза між повідомленнями
                    print(f"{Fore.YELLOW}[CLIENT {client_id}] → {message}")
                    await ws.send_str(message)

                # Почекати трохи перед закриттям
                await asyncio.sleep(2)

                # Закрити з'єднання
                await ws.close()
                receive_task.cancel()

                print(f"{Fore.YELLOW}[CLIENT {client_id}] Відключено")

    except Exception as e:
        print(f"{Fore.RED}[CLIENT {client_id}] Помилка: {e}")


# ============================================
# ДЕМОНСТРАЦІЇ
# ============================================

async def demo_basic_websocket():
    """Базова демонстрація WebSocket"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}ДЕМО 1: Базова робота WebSocket")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    # Запустити сервер
    server = await start_server()

    # Почекати трохи
    await asyncio.sleep(1)

    # Запустити клієнта
    await websocket_client(1, [
        "Привіт, сервере!",
        "Як справи?",
        "До побачення!"
    ])

    # Зупинити сервер
    await server.cleanup()
    print(f"\n{Fore.YELLOW}Сервер зупинено\n")


async def demo_multiple_clients():
    """Демонстрація кількох клієнтів"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}ДЕМО 2: Кілька клієнтів + Broadcast")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    # Запустити сервер
    server = await start_server()

    # Почекати трохи
    await asyncio.sleep(1)

    # Запустити кількох клієнтів паралельно
    await asyncio.gather(
        websocket_client(1, ["Клієнт 1: Привіт!", "Клієнт 1: Як справи?"]),
        websocket_client(2, ["Клієнт 2: Вітаю!", "Клієнт 2: Все добре!"]),
        websocket_client(3, ["Клієнт 3: Доброго дня!", "Клієнт 3: Чудово!"])
    )

    # Зупинити сервер
    await asyncio.sleep(1)
    await server.cleanup()
    print(f"\n{Fore.YELLOW}Сервер зупинено\n")


async def compare_http_vs_websocket():
    """Порівняння HTTP vs WebSocket"""
    print(f"\n{Fore.YELLOW}{'=' * 70}")
    print(f"{Fore.YELLOW}ПОРІВНЯННЯ: HTTP vs WebSocket")
    print(f"{Fore.YELLOW}{'=' * 70}\n")

    print(f"{Fore.CYAN}HTTP (Request-Response):")
    print(f"{Fore.WHITE}  ✓ Клієнт запитує → Сервер відповідає")
    print(f"{Fore.WHITE}  ✓ Просто у використанні")
    print(f"{Fore.WHITE}  ✗ Сервер не може ініціювати з'єднання")
    print(f"{Fore.WHITE}  ✗ Overhead для кожного запиту")
    print(f"{Fore.WHITE}  📊 Використання: REST API, веб-сторінки\n")

    print(f"{Fore.GREEN}WebSocket (Bidirectional):")
    print(f"{Fore.WHITE}  ✓ Постійне з'єднання")
    print(f"{Fore.WHITE}  ✓ Сервер може відправляти дані клієнту")
    print(f"{Fore.WHITE}  ✓ Низька затримка")
    print(f"{Fore.WHITE}  ✓ Менше overhead")
    print(f"{Fore.WHITE}  ✗ Складніше у реалізації")
    print(f"{Fore.WHITE}  📊 Використання: чати, real-time апдейти, ігри\n")


# ============================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================

async def main():
    """Запустити всі демонстрації"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}  МОДУЛЬ 6.3: WEBSOCKETS З AIOHTTP")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    # Порівняння
    await compare_http_vs_websocket()

    # Демо 1: Базовий WebSocket
    await demo_basic_websocket()

    # Демо 2: Кілька клієнтів
    await demo_multiple_clients()

    # Підсумок
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.GREEN}✅ Всі демонстрації завершено!")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    print(f"{Fore.YELLOW}📚 Ключові висновки:")
    print(f"{Fore.WHITE}  1. WebSocket: двостороннє постійне з'єднання")
    print(f"{Fore.WHITE}  2. Використовується для real-time застосунків")
    print(f"{Fore.WHITE}  3. Сервер може push повідомлення клієнтам")
    print(f"{Fore.WHITE}  4. Broadcast: відправити всім підключеним клієнтам")
    print(f"{Fore.WHITE}  5. aiohttp підтримує WebSocket out-of-the-box\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Програму зупинено користувачем")
