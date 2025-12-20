# Туторіал: Ваш перший скрепер з Beautiful Soup

Цей туторіал проведе вас через створення простого, але функціонального веб-скрепера. Ми будемо збирати цитати з сайту [quotes.toscrape.com](http://quotes.toscrape.com).

**Мета:** Видобути текст, автора та теги для кожної цитати на першій сторінці.

---

## Крок 1: Налаштування

Переконайтеся, що у вас встановлені необхідні бібліотеки. Якщо ні, відкрийте термінал і виконайте:
```bash
pip install requests beautifulsoup4
```

---

## Крок 2: Завантаження веб-сторінки

Створіть файл Python (наприклад, `scraper.py`) і додайте наступний код для завантаження вмісту сторінки.

```python
import requests

url = "http://quotes.toscrape.com"
try:
    response = requests.get(url)
    response.raise_for_status()  # Викликати виняток для поганих статус-кодів (4xx або 5xx)
    html_content = response.text
    print("Сторінку успішно завантажено!")
except requests.RequestException as e:
    print(f"Помилка завантаження сторінки: {e}")
    html_content = None
```

---

## Крок 3: Парсинг HTML за допомогою Beautiful Soup

Тепер розпарсимо завантажений HTML.

```python
from bs4 import BeautifulSoup

# Припускаючи, що html_content доступний з попереднього кроку
if html_content:
    soup = BeautifulSoup(html_content, 'html.parser')
    print("HTML успішно розпарсено!")
```

---

## Крок 4: Пошук цитат

Дослідіть HTML-код веб-сайту. Ви помітите, що кожна цитата міститься в `<div class="quote">`. Ми можемо використати це для пошуку всіх цитат.

```python
# ... всередині блоку `if html_content:`
quotes = soup.find_all('div', class_='quote')
print(f"Знайдено {len(quotes)} цитат на сторінці.")
```

---

## Крок 5: Видобування даних з кожної цитати

Тепер пройдемося по списку `quotes` і видобудемо текст, автора та теги з кожної цитати.

```python
# ... всередині блоку `if html_content:`
all_quotes_data = []
for quote in quotes:
    # Видобути текст
    text = quote.find('span', class_='text').get_text(strip=True)
    
    # Видобути автора
    author = quote.find('small', class_='author').get_text(strip=True)
    
    # Видобути теги
    tags_div = quote.find('div', class_='tags')
    tags = [tag.get_text(strip=True) for tag in tags_div.find_all('a', class_='tag')]
    
    all_quotes_data.append({
        'text': text,
        'author': author,
        'tags': tags
    })

# Вивести першу цитату для перевірки
if all_quotes_data:
    import json
    print("\nВидобута перша цитата:")
    print(json.dumps(all_quotes_data[0], indent=2, ensure_ascii=False))
```

---

## Крок 6: Повний скрипт

Ось повний, готовий до запуску скрипт.

```python
import requests
from bs4 import BeautifulSoup
import json

def scrape_quotes():
    """
    Скрапить цитати з першої сторінки quotes.toscrape.com.
    Повертає список словників, де кожен словник представляє цитату.
    """
    url = "http://quotes.toscrape.com"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Помилка завантаження сторінки: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all('div', class_='quote')
    
    if not quotes:
        print("Цитат не знайдено. Можливо, структура сайту змінилася.")
        return []
        
    all_quotes_data = []
    for quote in quotes:
        try:
            text = quote.find('span', class_='text').get_text(strip=True)
            author = quote.find('small', class_='author').get_text(strip=True)
            tags_div = quote.find('div', class_='tags')
            tags = [tag.get_text(strip=True) for tag in tags_div.find_all('a', class_='tag')]
            
            all_quotes_data.append({
                'text': text,
                'author': author,
                'tags': tags
            })
        except AttributeError:
            # Пропустити цитату, якщо її структура несподівана
            print("Попередження: не вдалося розпарсити цитату. Пропускаємо.")
            continue
            
    return all_quotes_data

if __name__ == '__main__':
    scraped_data = scrape_quotes()
    if scraped_data:
        print(f"Успішно зібрано {len(scraped_data)} цитат.")
        
        # Зберегти у файл JSON
        with open('quotes.json', 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        print("Дані збережено в quotes.json")
```

Тепер запустіть ваш файл `scraper.py`. Він виведе кількість зібраних цитат і збереже їх у файл `quotes.json` в тій же директорії. Вітаємо, ви створили свій перший веб-скрепер!
