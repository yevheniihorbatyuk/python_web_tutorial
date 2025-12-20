"""Spider for scraping books from books.toscrape.com"""

import scrapy
import logging
from decimal import Decimal
from datetime import datetime
from ..items import BookItem


class BooksSpider(scrapy.Spider):
    """
    Scrapes books from books.toscrape.com

    Usage:
        scrapy crawl books
        scrapy crawl books -o books.json
    """

    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'quotescrawler.pipelines.ValidationPipeline': 100,
            'quotescrawler.pipelines.DuplicatesPipeline': 200,
            'quotescrawler.pipelines.JsonExportPipeline': 300,
        },
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.book_count = 0
        self.categories = {}

    def parse(self, response):
        """Parse category list"""
        self.logger.info('Parsing category list')

        # Get all category links
        for category_link in response.css('a:contains("Books")').getall():
            # This is a simplified approach; actual categories are in sidebar
            pass

        # For now, just scrape books on first page with category detection
        yield response.follow('/catalogue/page-1.html', callback=self.parse_books)

    def parse_books(self, response):
        """Parse books from listing page"""
        self.logger.info(f'Parsing books from {response.url}')

        # Extract books from current page
        for book_li in response.css('ol.row li'):
            item = BookItem()

            # Extract data
            item['title'] = book_li.css('h3 a::attr(title)').get()
            price_text = book_li.css('p.price_color::text').get()
            item['price'] = price_text.replace('£', '') if price_text else None

            # Availability
            availability = book_li.css('p.instock.availability::text').getall()
            item['availability'] = availability[1].strip() if len(availability) > 1 else 'Unknown'

            # Rating
            rating_class = book_li.css('p.star-rating::attr(class)').get()
            item['rating'] = rating_class.replace('star-rating ', '') if rating_class else None

            # Category (from breadcrumbs or default)
            item['category'] = 'Books'
            item['description'] = ''
            item['source'] = self.name
            item['scraped_at'] = datetime.now().isoformat()

            if item['title']:
                self.book_count += 1
                self.logger.debug(f'Extracted book {self.book_count}: {item["title"]}')
                yield item

        # Follow pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            self.logger.debug(f'Following next page: {next_page}')
            yield response.follow(next_page, callback=self.parse_books)

    def closed(self, reason):
        """Called when spider closes"""
        self.logger.info(f'Spider closed. Total books scraped: {self.book_count}')
