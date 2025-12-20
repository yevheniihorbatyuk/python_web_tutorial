# Урок 1: Практичний веб-скрапінг з Beautiful Soup

Ласкаво просимо до першого уроку з веб-скрапінгу! Сьогодні ми навчимося "збирати" дані з веб-сайтів за допомогою Python. Це неймовірно корисна навичка для аналізу даних, моніторингу цін, агрегації новин та багато іншого.

## 1. Що таке веб-скрапінг і навіщо він потрібен?

Уявіть, що вам потрібно зібрати інформацію про 100 товарів з інтернет-магазину. Ви можете відкривати кожну сторінку вручну, копіювати дані та вставляти їх у таблицю. Це займе години.

**Веб-скрапінг** — це процес автоматизації цього завдання. Ми пишемо програму (скрипт), яка сама заходить на веб-сторінки, знаходить потрібну інформацію та зберігає її у структурованому форматі (наприклад, JSON або CSV).

**Основні інструменти, які ми будемо використовувати:**
- **Requests**: бібліотека для виконання HTTP-запитів, тобто для завантаження HTML-коду сторінок.
- **Beautiful Soup**: бібліотека для "парсингу" HTML. Вона перетворює хаотичний HTML-код на зручний об'єкт, по якому легко шукати потрібні дані.

---

## 2. Підготовка до роботи

Спочатку нам потрібно встановити необхідні бібліотеки. Відкрийте термінал і виконайте команду:

```bash
pip install requests beautifulsoup4
```

Ця команда завантажить та встановить `requests` і `beautifulsoup4`.

---

## 3. Основи HTML та CSS селекторів

Щоб ефективно знаходити дані, потрібно розуміти, як влаштовані веб-сторінки.

### Структура HTML

HTML (HyperText Markup Language) — це дерево тегів. Кожен тег має назву (наприклад, `<div>`, `<p>`, `<a>`) і може мати атрибути (`class`, `id`, `href`).

**Приклад:**
```html
<div class="quote">
    <span class="text">"Світ, який ми створили, є продуктом нашого мислення."</span>
    <span>
        by <small class="author">Альберт Ейнштейн</small>
    </span>
    <div class="tags">
        Теги:
        <a class="tag" href="/tag/change/">зміни</a>
        <a class="tag" href="/tag/thinking/">мислення</a>
    </div>
</div>
```

- **Теги:** `<div>`, `<span>`, `<small>`, `<a>`.
- **Атрибути:** `class="quote"`, `class="text"`, `href="/tag/change/"`.
- **Вміст:** Текст всередині тегів, наприклад, `"Світ, який ми створили..."`.

### Пошук елементів за допомогою CSS селекторів

Щоб знайти потрібний елемент, ми використовуємо "селектори". Це як адреса елемента на сторінці.

- `div` — знайти всі теги `<div>`.
- `.quote` — знайти всі теги з `class="quote"`.
- `#main` — знайти тег з `id="main"`.
- `div.quote` — знайти теги `<div>` з `class="quote"`.
- `div > p` — знайти теги `<p>`, які є прямими нащадками `<div>`.

---

## 4. Практичний приклад: Скрапінг цитат

Давайте напишемо скрипт, який збиратиме цитати, авторів та теги з сайту [quotes.toscrape.com](http://quotes.toscrape.com).

**Повний код знаходиться у файлі `code/01_beautiful_soup_practice.py`.** Тут ми розберемо його ключові частини.

### Крок 1: Завантаження HTML-сторінки

Ми створимо функцію, яка буде завантажувати HTML, імітуючи запит від браузера за допомогою `User-Agent`.

```python
import requests
import logging

log = logging.getLogger(__name__)

def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Перевірка на помилки (4xx/5xx)
        return response.text
    except requests.RequestException as e:
        log.error(f"Помилка при завантаженні URL {url}: {e}")
        return None
```

### Крок 2: Парсинг HTML та пошук даних

Після завантаження HTML ми використовуємо `BeautifulSoup` для його аналізу.

```python
from bs4 import BeautifulSoup, Tag

# ... всередині класу QuoteScraper ...

def _parse_quote(self, quote_tag: Tag) -> Optional[Dict]:
    """Парсить один тег <div> з цитатою."""
    try:
        # Знаходимо елемент <span class="text"> і отримуємо його текст
        text = quote_tag.find('span', class_='text').get_text(strip=True)
        
        # Знаходимо автора
        author = quote_tag.find('small', class_='author').get_text(strip=True)
        
        # Знаходимо всі теги і збираємо їх у список
        tags = [tag.get_text(strip=True) for tag in quote_tag.find_all('a', class_='tag')]

        return { 'text': text, 'author': author, 'tags': tags }
    except AttributeError:
        # Ця помилка виникне, якщо структура HTML несподівано змінилася
        log.warning("Не вдалося розпарсити цитату. Можливо, змінилася структура сайту.")
        return None
```
**Ключові методи `BeautifulSoup`:**
- `find('тег', class_='клас')`: знаходить перший елемент, що відповідає умові.
- `find_all('тег', class_='клас')`: знаходить всі елементи і повертає їх у вигляді списку.
- `.get_text(strip=True)`: отримує текстовий вміст тега, видаляючи зайві пробіли.

### Крок 3: Перехід по сторінках та збереження результатів

Хороший скрейпер повинен вміти обробляти декілька сторінок і бути "ввічливим" до сервера, роблячи невеликі затримки між запитами.

```python
import time

# ... всередині класу QuoteScraper ...

def scrape_site(self, max_pages: int = 5):
    """Скрапить сайт сторінка за сторінкою."""
    for page_num in range(1, max_pages + 1):
        url = f"{self.BASE_URL}/page/{page_num}/"
        html = fetch_html(url)
        # ... (код для парсингу) ...

        # Перевіряємо, чи є кнопка "Next", щоб знати, чи є наступні сторінки
        soup = BeautifulSoup(html, 'html.parser')
        if not soup.find('li', class_='next'):
            log.info("Це остання сторінка.")
            break
        
        # Робимо затримку, щоб не перевантажувати сервер
        time.sleep(1)
```

### Крок 4: Збереження даних у JSON

Зібрані дані найзручніше зберігати у форматі JSON.

```python
import json

# ... всередині класу QuoteScraper ...

def save_to_json(self, filename: str = "quotes.json"):
    """Зберігає зібрані цитати у файл JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(self.quotes, f, indent=2, ensure_ascii=False)
```
- `indent=2`: робить JSON-файл читабельним.
- `ensure_ascii=False`: важливо для коректного збереження кириличних символів.

---

## 5. Етика та найкращі практики

- **Будьте ввічливими:** Завжди робіть затримки (`time.sleep()`) між запитами. 1-2 секунди — це хороша практика.
- **Перевіряйте `robots.txt`:** Це файл на сайті (напр., `quotes.toscrape.com/robots.txt`), де власники вказують, які сторінки можна і не можна скрапити.
- **Використовуйте `User-Agent`:** Це робить ваш запит схожим на запит від реального браузера.
- **Не скрапте персональні дані:** Поважайте приватність.
- **Обробляйте помилки:** Сайти змінюються. Ваш код повинен бути готовим до того, що елемент не буде знайдено.

---

## 6. Корисні посилання

- **[Офіційна документація Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)**: Найкраще джерело інформації.
- **[Документація бібліотеки Requests](https://requests.readthedocs.io/en/latest/)**: Все про HTTP-запити.
- **[CSS Selectors Reference](https://www.w3schools.com/cssref/css_selectors.php)**: Чудовий довідник по селекторах.
- **[Сайт для практики скрапінгу](http://toscrape.com/)**: Містить декілька прикладів сайтів, спеціально створених для тренувань.

Тепер ви готові запустити скрипт `code/01_beautiful_soup_practice.py` і побачити, як він працює вживу!
```bash
python 01_beginner_edition/code/01_beautiful_soup_practice.py
```
