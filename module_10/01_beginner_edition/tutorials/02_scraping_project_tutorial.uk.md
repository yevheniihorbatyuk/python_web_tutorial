# Туторіал: Створення надійного скрепера

Цей туторіал демонструє, як створити більш просунутий скрепер, використовуючи концепції з теоретичного уроку. Ми будемо використовувати код з `code/02_real_world_scraping.py` як наш довідник.

**Мета:** Скрапити цитати, обробляти помилки та зберігати дані в базу даних SQLite.

---

## Крок 1: Розуміння структури коду

Відкрийте `code/02_real_world_scraping.py`. Він містить три основні класи:
- **`Article`**: `dataclass` для зберігання зібраних даних.
- **`ArticleDatabase`**: керує всіма взаємодіями з базою даних SQLite.
- **`RobustScraper`**: основний клас скрепера, який включає логіку повторних спроб.

---

## Крок 2: Запуск скрепера

Скрипт призначений для прямого запуску. Відкрийте термінал і виконайте:
```bash
python 01_beginner_edition/code/02_real_world_scraping.py
```

### Що відбувається під час запуску?

1.  Викликається функція `main_workflow()`.
2.  Створюється екземпляр `RobustScraper`.
3.  Скрепер завантажує HTML з `quotes.toscrape.com`, автоматично повторюючи спроби в разі невдачі.
4.  Він парсить цитати та зберігає їх як об'єкти `Article`.
5.  Створюється екземпляр `ArticleDatabase`, який також створює файл `articles.db`, якщо він не існує.
6.  Зібрані статті зберігаються в базу даних. Дублікати (на основі URL) автоматично пропускаються.
7.  Скрипт логує свій прогрес у консоль.

---

## Крок 3: Пояснення ключового коду

### Метод `_fetch_with_retry`

Це ядро надійного скрепера. Він обгортає `requests.get()` у цикл.

```python
# Всередині класу RobustScraper
def _fetch_with_retry(self, url: str) -> Optional[str]:
    for attempt in range(self.max_retries):
        try:
            # ... requests.get(url) ...
            return response.text
        except requests.RequestException as e:
            log.warning(f"Спроба {attempt + 1} не вдалася.")
            if attempt < self.max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                log.error("Не вдалося після всіх спроб.")
                return None
```

### Клас `ArticleDatabase`

Цей клас обробляє всю логіку бази даних, відокремлюючи її від коду скрапінгу.

```python
# Всередині класу ArticleDatabase
def save_articles(self, articles: List[Article]) -> int:
    saved_count = 0
    cursor = self.conn.cursor()
    for article in articles:
        try:
            # Обмеження UNIQUE на колонці 'url' запобігає дублікатам
            cursor.execute("INSERT INTO ...", (...))
            saved_count += 1
        except sqlite3.IntegrityError:
            # Ця помилка очікувана, якщо URL вже існує
            log.warning(f"Стаття з URL {article.url} вже існує.")
    
    self.conn.commit()
    return saved_count
```

---

## Крок 4: Перевірка результату

Після запуску скрипта ви знайдете новий файл з назвою `articles.db` у каталозі проєкту. Це ваша база даних SQLite.

Ви можете перевірити її за допомогою інструменту для баз даних, такого як [DB Browser for SQLite](https://sqlitebrowser.org/), або безпосередньо з командного рядка:

```bash
# Встановіть інструмент командного рядка SQLite, якщо у вас його немає
# (На Ubuntu: sudo apt-get install sqlite3)

# Відкрийте базу даних
sqlite3 articles.db

# Виконайте кілька SQL-запитів
sqlite> .tables
articles

sqlite> SELECT COUNT(*) FROM articles;
30

sqlite> SELECT author, title FROM articles LIMIT 3;
Albert Einstein|"The world as we have created it is a process of our thinking..."
J.K. Rowling|"It is our choices, Harry, that show what we truly are, far more than our abilities."
Albert Einstein|"There are only two ways to live your life. One is as though nothing is a miracle..."

sqlite> .quit
```

Кожного разу, коли ви запускаєте скрипт, він додаватиме лише нові статті, якщо знайде їх, завдяки обмеженню `UNIQUE` на URL.
