# Туторіал: Початок роботи зі Scrapy

**Мета**: Створити та запустити вашого першого павука Scrapy.

---

## Налаштування

1.  **Перейдіть до каталогу проєкту Scrapy**:
    ```bash
    cd /root/goit/python_web/module_10/02_advanced_edition/code/scrapy_project
    ```
2.  **Перевірте структуру проєкту**: Ви повинні побачити файл `scrapy.cfg` та каталог `quotescrawler`.

---

## Крок 1: Запуск вашого першого павука

Команди Scrapy виконуються з кореневого каталогу проєкту.

### 1a. Запуск павука

Команда `crawl` запускає павука.
```bash
scrapy crawl quotes
```
Ви побачите логи, як павук завантажує сторінки та видобуває дані.

### 1b. Збереження виводу у файл

Ви можете зберегти зібрані дані безпосередньо у файл (наприклад, JSON, CSV).
```bash
scrapy crawl quotes -o quotes.json
```
Це створить файл `quotes.json` з результатами.

---

## Крок 2: Розуміння коду павука

Відкрийте `quotescrawler/spiders/quotes_spider.py`.

```python
class QuotesSpider(scrapy.Spider):
    # Унікальне ім'я для павука
    name = 'quotes'
    # Домени, які цьому павуку дозволено кроулити
    allowed_domains = ['quotes.toscrape.com']
    # URL-адреси, з яких павук почне кроулінг
    start_urls = ['https://quotes.toscrape.com/']

    def parse(self, response):
        """
        Цей метод викликається для обробки відповіді, завантаженої для кожного
        зробленого запиту.
        """
        # Пройтися по кожному елементу цитати на сторінці
        for quote_div in response.css('div.quote'):
            # Повернути словник з видобутими даними
            yield {
                'text': quote_div.css('span.text::text').get(),
                'author': quote_div.css('small.author::text').get(),
            }

        # Знайти посилання на наступну сторінку та перейти за ним
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
```
- **`yield`**: У Scrapy `yield` використовується для повернення видобутих даних або для повернення нових запитів для переходу.

---

## Крок 3: Інтерактивне тестування за допомогою Scrapy Shell

`shell` — це інтерактивна консоль, яка дозволяє тестувати ваші селектори на живій сторінці.

1.  **Запустіть shell**:
    ```bash
    scrapy shell 'https://quotes.toscrape.com'
    ```
2.  **Тестуйте ваші селектори**: Усередині shell у вас є доступ до об'єкта `response`.
    ```python
    # Отримати заголовок сторінки
    >>> response.css('title::text').get()
    'Quotes to Scrape'

    # Отримати текст першої цитати
    >>> response.css('div.quote span.text::text').get()
    '"The world as we have created it is a process of our thinking..."'
    ```

Це найкращий спосіб визначити правильні селектори перед написанням вашого павука.
