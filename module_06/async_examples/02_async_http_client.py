"""
Модуль 6.2: Асинхронні HTTP запити з aiohttp
==============================================

Цей модуль демонструє:
1. Різницю між requests (sync) та aiohttp (async)
2. Паралельне завантаження декількох сайтів
3. Вимірювання швидкості для важких та легких сайтів
4. Практичні можливості aiohttp
"""

import asyncio
import time
from typing import List, Dict
import aiohttp
import requests
from colorama import Fore, Style, init

# Ініціалізація colorama
init(autoreset=True)


# ============================================
# ТЕСТОВІ URL
# ============================================

# Легкі сайти (швидкі відповіді)
LIGHT_SITES = [
    "https://httpbin.org/delay/0",
    "https://httpbin.org/get",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/users/1",
    "https://api.github.com",
]

# Важкі сайти (повільні відповіді)
HEAVY_SITES = [
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/3",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/2",
]

# Реальні API для тестування
REAL_APIS = [
    "https://api.github.com/users/github",
    "https://api.github.com/users/microsoft",
    "https://api.github.com/users/google",
    "https://jsonplaceholder.typicode.com/posts",
    "https://jsonplaceholder.typicode.com/users",
]


# ============================================
# 1. СИНХРОННИЙ ПІДХІД (requests)
# ============================================

def fetch_url_sync(url: str) -> Dict:
    """Синхронне завантаження URL через requests"""
    start = time.time()
    try:
        response = requests.get(url, timeout=10)
        duration = time.time() - start
        return {
            "url": url,
            "status": response.status_code,
            "duration": duration,
            "size": len(response.content),
            "success": True
        }
    except Exception as e:
        duration = time.time() - start
        return {
            "url": url,
            "error": str(e),
            "duration": duration,
            "success": False
        }


def fetch_multiple_sync(urls: List[str]) -> List[Dict]:
    """Синхронне завантаження кількох URL"""
    print(f"\n{Fore.RED}{'=' * 70}")
    print(f"{Fore.RED}СИНХРОННИЙ ПІДХІД (requests) - послідовне завантаження")
    print(f"{Fore.RED}{'=' * 70}\n")

    start = time.time()
    results = []

    for i, url in enumerate(urls, 1):
        print(f"{Fore.YELLOW}[{i}/{len(urls)}] Завантаження {url[:50]}...")
        result = fetch_url_sync(url)
        results.append(result)
        status = f"{Fore.GREEN}✓" if result['success'] else f"{Fore.RED}✗"
        print(f"{status} {result['duration']:.2f}с")

    total_duration = time.time() - start

    print(f"\n{Fore.RED}⏱️  Загальний час: {total_duration:.2f}с")
    print(f"{Fore.RED}📊 Середній час на запит: {total_duration/len(urls):.2f}с\n")

    return results


# ============================================
# 2. АСИНХРОННИЙ ПІДХІД (aiohttp)
# ============================================

async def fetch_url_async(session: aiohttp.ClientSession, url: str) -> Dict:
    """Асинхронне завантаження URL через aiohttp"""
    start = time.time()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            content = await response.read()
            duration = time.time() - start
            return {
                "url": url,
                "status": response.status,
                "duration": duration,
                "size": len(content),
                "success": True
            }
    except Exception as e:
        duration = time.time() - start
        return {
            "url": url,
            "error": str(e),
            "duration": duration,
            "success": False
        }


async def fetch_multiple_async(urls: List[str]) -> List[Dict]:
    """Асинхронне завантаження кількох URL"""
    print(f"\n{Fore.GREEN}{'=' * 70}")
    print(f"{Fore.GREEN}АСИНХРОННИЙ ПІДХІД (aiohttp) - паралельне завантаження")
    print(f"{Fore.GREEN}{'=' * 70}\n")

    start = time.time()

    # Створити сесію для повторного використання з'єднань
    async with aiohttp.ClientSession() as session:
        # Запустити всі запити паралельно
        print(f"{Fore.CYAN}🚀 Запускаю {len(urls)} запитів паралельно...\n")

        tasks = [fetch_url_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

        # Показати результати
        for i, result in enumerate(results, 1):
            status = f"{Fore.GREEN}✓" if result['success'] else f"{Fore.RED}✗"
            url_short = result['url'][:50]
            print(f"{status} [{i}/{len(urls)}] {url_short}: {result['duration']:.2f}с")

    total_duration = time.time() - start

    print(f"\n{Fore.GREEN}⏱️  Загальний час: {total_duration:.2f}с")
    print(f"{Fore.GREEN}📊 Середній час на запит: {total_duration/len(urls):.2f}с\n")

    return results


# ============================================
# 3. ПОРІВНЯННЯ SYNC VS ASYNC
# ============================================

async def compare_sync_vs_async(urls: List[str], description: str) -> None:
    """Порівняти синхронний та асинхронний підходи"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}ПОРІВНЯННЯ: {description}")
    print(f"{Fore.CYAN}{'=' * 70}")

    # Синхронний підхід
    sync_start = time.time()
    sync_results = fetch_multiple_sync(urls)
    sync_duration = time.time() - sync_start

    # Асинхронний підхід
    async_start = time.time()
    async_results = await fetch_multiple_async(urls)
    async_duration = time.time() - async_start

    # Результати порівняння
    speedup = sync_duration / async_duration if async_duration > 0 else 0

    print(f"{Fore.YELLOW}{'=' * 70}")
    print(f"{Fore.YELLOW}📊 РЕЗУЛЬТАТИ ПОРІВНЯННЯ")
    print(f"{Fore.YELLOW}{'=' * 70}")
    print(f"{Fore.RED}Синхронний (requests):  {sync_duration:.2f}с")
    print(f"{Fore.GREEN}Асинхронний (aiohttp):  {async_duration:.2f}с")
    print(f"{Fore.CYAN}🚀 Прискорення:          {speedup:.2f}x швидше!")
    print(f"{Fore.CYAN}⏱️  Економія часу:       {sync_duration - async_duration:.2f}с")
    print(f"{Fore.YELLOW}{'=' * 70}\n")


# ============================================
# 4. ДОДАТКОВІ МОЖЛИВОСТІ AIOHTTP
# ============================================

async def advanced_aiohttp_features() -> None:
    """Демонстрація додаткових можливостей aiohttp"""
    print(f"\n{Fore.MAGENTA}{'=' * 70}")
    print(f"{Fore.MAGENTA}ДОДАТКОВІ МОЖЛИВОСТІ AIOHTTP")
    print(f"{Fore.MAGENTA}{'=' * 70}\n")

    async with aiohttp.ClientSession() as session:
        # 1. POST запит
        print(f"{Fore.CYAN}1. POST запит з JSON даними:")
        async with session.post(
            'https://httpbin.org/post',
            json={'name': 'Python', 'course': 'Web Development'}
        ) as response:
            data = await response.json()
            print(f"{Fore.GREEN}   Статус: {response.status}")
            print(f"{Fore.GREEN}   Відправлено: {data['json']}\n")

        # 2. Заголовки
        print(f"{Fore.CYAN}2. Запит з кастомними заголовками:")
        headers = {'User-Agent': 'Python Course Bot 1.0'}
        async with session.get('https://httpbin.org/headers', headers=headers) as response:
            data = await response.json()
            print(f"{Fore.GREEN}   User-Agent: {data['headers'].get('User-Agent', 'N/A')}\n")

        # 3. Query параметри
        print(f"{Fore.CYAN}3. Запит з query параметрами:")
        params = {'page': 1, 'limit': 10}
        async with session.get('https://httpbin.org/get', params=params) as response:
            data = await response.json()
            print(f"{Fore.GREEN}   URL: {data['url']}\n")

        # 4. Timeout
        print(f"{Fore.CYAN}4. Запит з timeout:")
        try:
            timeout = aiohttp.ClientTimeout(total=2)
            async with session.get('https://httpbin.org/delay/5', timeout=timeout) as response:
                print(f"{Fore.GREEN}   Успішно")
        except asyncio.TimeoutError:
            print(f"{Fore.YELLOW}   ⏱️  Timeout після 2с (очікувано)\n")


# ============================================
# 5. ПРАКТИЧНИЙ ПРИКЛАД: Web Scraper
# ============================================

async def fetch_github_user(session: aiohttp.ClientSession, username: str) -> Dict:
    """Завантажити інформацію про користувача GitHub"""
    url = f"https://api.github.com/users/{username}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "username": data["login"],
                    "name": data.get("name", "N/A"),
                    "followers": data["followers"],
                    "repos": data["public_repos"],
                    "success": True
                }
            else:
                return {"username": username, "success": False, "error": f"Status {response.status}"}
    except Exception as e:
        return {"username": username, "success": False, "error": str(e)}


async def github_scraper_example() -> None:
    """Приклад: завантажити дані про кількох GitHub користувачів"""
    print(f"\n{Fore.MAGENTA}{'=' * 70}")
    print(f"{Fore.MAGENTA}ПРАКТИЧНИЙ ПРИКЛАД: GitHub Scraper")
    print(f"{Fore.MAGENTA}{'=' * 70}\n")

    usernames = ["github", "microsoft", "google", "facebook", "python"]

    start = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_github_user(session, username) for username in usernames]
        results = await asyncio.gather(*tasks)

    duration = time.time() - start

    print(f"{Fore.CYAN}Результати ({duration:.2f}с):\n")
    for user in results:
        if user['success']:
            print(f"{Fore.GREEN}✓ {user['username']:15} | "
                  f"{user['name']:20} | "
                  f"Followers: {user['followers']:6} | "
                  f"Repos: {user['repos']:4}")
        else:
            print(f"{Fore.RED}✗ {user['username']:15} | Error: {user['error']}")

    print(f"\n{Fore.YELLOW}📊 Завантажено {len(results)} профілів за {duration:.2f}с")
    print(f"{Fore.YELLOW}⚡ Середній час: {duration/len(results):.2f}с на профіль\n")


# ============================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================

async def main() -> None:
    """Запустити всі демонстрації"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}  МОДУЛЬ 6.2: АСИНХРОННІ HTTP ЗАПИТИ З AIOHTTP")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    # 1. Порівняння на легких сайтах
    await compare_sync_vs_async(LIGHT_SITES, "Легкі сайти (швидкі відповіді)")

    # 2. Порівняння на важких сайтах
    await compare_sync_vs_async(HEAVY_SITES, "Важкі сайти (повільні відповіді)")

    # 3. Додаткові можливості
    await advanced_aiohttp_features()

    # 4. Практичний приклад
    await github_scraper_example()

    # Підсумок
    print(f"{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.GREEN}✅ Всі приклади завершено!")
    print(f"{Fore.CYAN}{'=' * 70}\n")

    print(f"{Fore.YELLOW}📚 Ключові висновки:")
    print(f"{Fore.WHITE}  1. requests (sync): послідовні запити, повільно")
    print(f"{Fore.WHITE}  2. aiohttp (async): паралельні запити, швидко")
    print(f"{Fore.WHITE}  3. Прискорення: 5-10x для множинних запитів")
    print(f"{Fore.WHITE}  4. aiohttp підтримує: GET, POST, headers, timeout і більше")
    print(f"{Fore.WHITE}  5. Використовуйте ClientSession для кількох запитів\n")


if __name__ == "__main__":
    # Запустити головну async функцію
    asyncio.run(main())
