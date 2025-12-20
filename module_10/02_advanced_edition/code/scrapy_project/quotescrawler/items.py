"""Data item classes for quotescrawler"""

import scrapy


class QuoteItem(scrapy.Item):
    """Item for scraped quotes"""
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    source = scrapy.Field()
    scraped_at = scrapy.Field()


class BookItem(scrapy.Item):
    """Item for scraped books"""
    title = scrapy.Field()
    price = scrapy.Field()
    availability = scrapy.Field()
    rating = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    source = scrapy.Field()
    scraped_at = scrapy.Field()
