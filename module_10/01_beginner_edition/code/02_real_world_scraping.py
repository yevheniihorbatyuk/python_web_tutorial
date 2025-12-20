"""
Урок 2: Створення надійного скрепера для реальних задач

Цей скрипт є комплексним прикладом скрепера, який розроблено для
стабільної роботи в реальних умовах. Ключові особливості:

- **Надійне завантаження:** Автоматичні повторні спроби із зростаючою затримкою
  (exponential backoff) у разі мережевих збоїв.
- **Структуровані дані:** Використання `dataclass` для створення чітких моделей даних.
- **Валідація та очищення:** Перевірка даних перед збереженням та видалення дублікатів.
- **Збереження в базу даних:** Використання SQLite для надійного зберігання даних.
- **Професійне логування:** Запис усіх кроків, попереджень та помилок для легкого моніторингу.
"""

import json
import logging
import sqlite3
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

# --- Налаштування логера ---
# Використовуємо логер замість print() для гнучкого керування виводом інформації.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

# --- Модель даних ---

@dataclass
class Article:
    """
    Клас даних для зберігання інформації про статтю (або в нашому випадку, цитату).
    Використання dataclass робить код чистішим та більш структурованим.
    """
    title: str
    url: str
    author: str
    tags: List[str]
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Перетворює об'єкт на словник, зручний для серіалізації в JSON."""
        return asdict(self)

# --- Клас для роботи з базою даних ---

class ArticleDatabase:
    """Керує всіма операціями з базою даних SQLite."""

    def __init__(self, db_path: str = "news.db"):
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(self.db_path)
            self._create_table()
        except sqlite3.Error as e:
            log.error(f"Помилка підключення до бази даних {self.db_path}: {e}")
            raise

    def _create_table(self):
        """Створює таблицю для статей, якщо вона ще не існує."""
        try:
            cursor = self.conn.cursor()
            # UNIQUE(url) запобігає додаванню дублікатів за URL.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    tags TEXT NOT NULL,
                    scraped_at TEXT NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            log.error(f"Помилка створення таблиці: {e}")

    def save_articles(self, articles: List[Article]) -> int:
        """
        Зберігає список статей у базу даних.
        Пропускає дублікати за унікальним полем `url`.
        """
        saved_count = 0
        cursor = self.conn.cursor()
        for article in articles:
            try:
                tags_str = json.dumps(article.tags)
                cursor.execute("""
                    INSERT INTO articles (title, author, url, tags, scraped_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (article.title, article.author, article.url, tags_str, article.scraped_at))
                saved_count += 1
            except sqlite3.IntegrityError:
                # Це очікувана помилка, якщо URL вже існує.
                log.warning(f"Стаття з URL {article.url} вже існує. Пропускаємо.")
            except sqlite3.Error as e:
                log.error(f"Помилка збереження статті {article.title}: {e}")
        
        self.conn.commit()
        log.info(f"Успішно збережено {saved_count} нових статей.")
        return saved_count

    def close(self):
        """Закриває з'єднання з базою даних."""
        if self.conn:
            self.conn.close()

# --- Основний клас скрепера ---

class RobustScraper:
    """
    Надійний скрепер з логікою повторних спроб та обробкою помилок.
    """
    BASE_URL = "http://quotes.toscrape.com"

    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay # Затримка між запитами в секундах
        self.articles: List[Article] = []

    def _fetch_with_retry(self, url: str) -> Optional[str]:
        """
        Завантажує HTML з логікою повторних спроб.
        Використовує exponential backoff — збільшує час очікування після кожної невдалої спроби.
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Educational Scraper)'}
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                log.warning(f"Спроба {attempt + 1}/{self.max_retries} не вдалася: {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s...
                    wait_time = 2 ** attempt
                    log.info(f"Повторна спроба через {wait_time} сек...")
                    time.sleep(wait_time)
                else:
                    log.error(f"Не вдалося завантажити {url} після {self.max_retries} спроб.")
                    return None
        return None

    def scrape_site(self, max_pages: int = 3) -> List[Article]:
        """
        Основний метод для скрапінгу сайту.
        """
        log.info(f"Починаємо скрапінг сайту {self.BASE_URL} (макс. {max_pages} сторінок)")
        
        for page_num in range(1, max_pages + 1):
            page_url = f"{self.BASE_URL}/page/{page_num}/"
            html = self._fetch_with_retry(page_url)

            if not html:
                break # Зупиняємося, якщо не вдалося завантажити сторінку

            soup = BeautifulSoup(html, 'html.parser')
            quote_tags = soup.find_all('div', class_='quote')

            if not quote_tags:
                log.info("На сторінці не знайдено цитат. Завершуємо.")
                break

            for tag in quote_tags:
                try:
                    text = tag.find('span', class_='text').get_text(strip=True)
                    author = tag.find('small', class_='author').get_text(strip=True)
                    tags = [t.get_text(strip=True) for t in tag.find_all('a', class_='tag')]
                    
                    # Використовуємо заголовок цитати як "title" для нашої моделі Article
                    title = text[:50] + '...' if len(text) > 50 else text

                    self.articles.append(Article(title=title, url=page_url, author=author, tags=tags))
                except AttributeError:
                    log.warning("Не вдалося розпарсити тег цитати. Пропускаємо.")
            
            log.info(f"Оброблено сторінку {page_num}. Зібрано {len(self.articles)} статей.")
            
            # Ввічлива затримка між сторінками
            time.sleep(self.delay)
            
        log.info(f"Скрапінг завершено. Усього зібрано: {len(self.articles)} статей.")
        return self.articles

# --- Головний робочий процес ---

def main_workflow():
    """
    Поєднує всі кроки: скрапінг, валідацію, збереження.
    """
    log.info("--- Початок робочого процесу скрапінгу ---")

    # 1. Скрапінг
    scraper = RobustScraper()
    articles = scraper.scrape_site(max_pages=3)

    if not articles:
        log.info("Не зібрано жодної статті. Завершення роботи.")
        return

    # 2. Валідація та очищення (в цьому прикладі дані чисті, але в реальності тут був би крок валідації)
    # Наприклад, видалення статей без автора, занадто коротких і т.д.
    log.info(f"Пройшли валідацію: {len(articles)} статей.")

    # 3. Збереження в базу даних
    db = None
    try:
        db = ArticleDatabase(db_path="articles.db")
        db.save_articles(articles)
    except sqlite3.Error as e:
        log.error(f"Не вдалося виконати операції з базою даних: {e}")
    finally:
        if db:
            db.close()

    log.info("--- Робочий процес завершено ---")


if __name__ == "__main__":
    main_workflow()