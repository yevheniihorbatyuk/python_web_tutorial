"""
Павук для скрапінгу цитат з сайту quotes.toscrape.com
"""

import scrapy
import logging
from datetime import datetime
from ..items import QuoteItem


class QuotesSpider(scrapy.Spider):
    """
    Скрапить цитати з quotes.toscrape.com

    Використання:
        scrapy crawl quotes
        scrapy crawl quotes -o quotes.json
    """
    # Ім'я павука, унікальне в межах проєкту
    name = 'quotes'
    
    # Домени, на які павуку дозволено переходити
    allowed_domains = ['quotes.toscrape.com']
    
    # Початкові URL, з яких павук починає роботу
    start_urls = ['https://quotes.toscrape.com/']

    # Кастомні налаштування для цього павука
    custom_settings = {
        'ITEM_PIPELINES': {
            # Кожен 'item' буде проходити через ці конвеєри (pipelines)
            'quotescrawler.pipelines.ValidationPipeline': 100,
            'quotescrawler.pipelines.DuplicatesPipeline': 200,
            'quotescrawler.pipelines.JsonExportPipeline': 300,
        },
        'LOG_LEVEL': 'INFO', # Рівень логування
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.quote_count = 0

    def parse(self, response):
        """
        Основний метод-обробник. Він парсить відповідь (response),
        видобуває дані та знаходить нові посилання для переходу.
        """
        self.logger.info(f'Парсинг сторінки: {response.url}')

        # Використовуємо CSS-селектори для пошуку всіх блоків з цитатами
        for quote_div in response.css('div.quote'):
            # Створюємо екземпляр QuoteItem для зберігання даних
            item = QuoteItem()
            
            # Видобуваємо дані за допомогою CSS-селекторів
            item['text'] = quote_div.css('span.text::text').get()
            item['author'] = quote_div.css('small.author::text').get()
            item['tags'] = quote_div.css('a.tag::text').getall()
            item['source'] = self.name
            item['scraped_at'] = datetime.now().isoformat()

            self.quote_count += 1
            self.logger.debug(f'Видобуто цитату №{self.quote_count}: {item["text"][:50]}...')

            # 'yield' відправляє 'item' до конвеєра (Item Pipelines)
            yield item

        # Знаходимо посилання на наступну сторінку (пагінація)
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            self.logger.debug(f'Перехід на наступну сторінку: {next_page}')
            # 'yield response.follow' створює новий запит на наступну сторінку,
            # і після завантаження викликає цей же метод 'parse'
            yield response.follow(next_page, callback=self.parse)

    def closed(self, reason):
        """Цей метод викликається, коли павук завершує роботу."""
        self.logger.info(f'Павук завершив роботу. Усього зібрано цитат: {self.quote_count}')