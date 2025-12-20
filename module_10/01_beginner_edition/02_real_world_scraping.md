# Урок 2: Створення надійного скрепера

На першому уроці ми ознайомилися з основами. Тепер час створити щось, що буде стабільно працювати в реальних умовах. Професійний скрепер — це не просто запит і парсинг. Це також обробка помилок, збереження даних і "ввічлива" поведінка в мережі.

## 1. Проблеми реального світу

Коли ви починаєте скрапити справжні сайти, ви стикаєтеся з проблемами:
- **Мережеві збої:** Інтернет-з'єднання може бути нестабільним.
- **Сайт тимчасово недоступний:** Сервер може не відповідати.
- **Блокування:** Сайт може заблокувати вас, якщо ви робите занадто багато запитів.
- **Зміна структури HTML:** Сайт оновили, і ваші селектори більше не працюють.
- **"Брудні" дані:** Відсутні поля, дублікати, неправильний формат.

Наш сьогоднішній скрипт буде вирішувати ці проблеми.

---

## 2. Архітектура надійного скрепера

Ми побудуємо наш скрипт за наступними принципами:

1.  **Модель даних (`dataclass`):** Чітко визначаємо, яку інформацію ми збираємо.
2.  **Клас для роботи з БД:** Інкапсулюємо всю логіку роботи з базою даних в одному місці.
3.  **Основний клас скрепера:** Він відповідає за завантаження та парсинг, включаючи логіку повторних спроб.
4.  **Головний робочий процес (`main_workflow`):** Функція, яка координує всі кроки.

**Повний код знаходиться у файлі `code/02_real_world_scraping.py`.**

---

## 3. Ключові компоненти

### Надійне завантаження з `retry` логікою

Мережа ненадійна. Якщо запит не вдався, не варто одразу здаватися. Ми реалізуємо механізм **exponential backoff**: якщо спроба невдала, ми чекаємо 1 секунду. Якщо і друга невдала — чекаємо 2 секунди, потім 4, і так далі.

```python
# ... всередині класу RobustScraper ...

def _fetch_with_retry(self, url: str) -> Optional[str]:
    headers = {'User-Agent': 'Mozilla/5.0 (Educational Scraper)'}
    for attempt in range(self.max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status() # Перевірка на HTTP помилки
            return response.text
        except requests.RequestException as e:
            log.warning(f"Спроба {attempt + 1}/{self.max_retries} не вдалася: {e}")
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt # 1, 2, 4...
                log.info(f"Повторна спроба через {wait_time} сек...")
                time.sleep(wait_time)
            else:
                log.error(f"Не вдалося завантажити {url} після {self.max_retries} спроб.")
                return None
    return None
```

### Структурування даних з `dataclass`

Замість того, щоб працювати зі словниками, ми створимо чітку модель даних. Це робить код більш читабельним, безпечним і легким для підтримки.

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Article:
    title: str
    url: str
    author: str
    tags: List[str]
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

### Збереження даних в SQLite

Зберігати результати в файлі — це добре для початку, але для надійності потрібна база даних. SQLite — ідеальний вибір для невеликих та середніх проектів, оскільки вона не потребує окремого сервера.

Ми створимо клас `ArticleDatabase`, який буде відповідати за:
- Створення таблиці.
- Збереження статей, автоматично пропускаючи дублікати за унікальним `URL`.

```python
# ... всередині класу ArticleDatabase ...

def _create_table(self):
    cursor = self.conn.cursor()
    # UNIQUE(url) гарантує, що ми не додамо одну й ту саму статтю двічі
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
```

### Професійне логування

Замість `print()` ми використовуємо стандартний модуль `logging`. Це дозволяє:
- **Встановлювати рівні важливості:** `INFO`, `WARNING`, `ERROR`.
- **Додавати часові мітки:** Бачити, коли саме відбулася подія.
- **Гнучко налаштовувати вивід:** Писати логи у файл, в консоль, або і туди, і туди.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

# Приклади використання
log.info("Починаємо скрапінг...")
log.warning("Не вдалося розпарсити тег.")
log.error("Не вдалося завантажити сторінку.")
```

---

## 4. Запуск та результати

Щоб запустити повний процес, виконайте команду в терміналі:

```bash
python 01_beginner_edition/code/02_real_world_scraping.py
```

Скрипт виконає наступні кроки:
1.  Запустить скрепер, який збере 3 сторінки цитат.
2.  Виведе в консоль логи про свій прогрес.
3.  Створить (або оновить) файл `articles.db` з зібраними даними.

Ви можете переглянути вміст бази даних за допомогою будь-якого SQLite-браузера (наприклад, [DB Browser for SQLite](https://sqlitebrowser.org/)).

---

## 5. Корисні посилання

- **[Python `dataclasses`](https://docs.python.org/3/library/dataclasses.html)**: Офіційна документація.
- **[Python `logging` HOWTO](https://docs.python.org/3/howto/logging.html)**: Практичний посібник з логування.
- **[Python `sqlite3` module](https://docs.python.org/3/library/sqlite3.html)**: Робота з SQLite в Python.
- **[Tenacity](https://tenacity.readthedocs.io/en/latest/)**: Потужна бібліотека для реалізації логіки повторних спроб.

На цьому уроці ми створили фундамент для написання надійних скреперів. Наступним кроком буде інтеграція наших даних у веб-додаток.
