# Scrapy settings for quotescrawler project
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/settings.html

BOT_NAME = 'quotescrawler'

SPIDER_MODULES = ['quotescrawler.spiders']
NEWSPIDER_MODULE = 'quotescrawler.spiders'

# Crawl responsibly by identifying yourself
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests per domain. Default is 8.
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Delay between consecutive requests to the same domain
DOWNLOAD_DELAY = 1

# Disable cookies (not needed for this use case)
COOKIES_ENABLED = False

# Retry configuration
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504]

# Item pipelines
ITEM_PIPELINES = {
    'quotescrawler.pipelines.ValidationPipeline': 100,
    'quotescrawler.pipelines.DuplicatesPipeline': 200,
    'quotescrawler.pipelines.JsonExportPipeline': 300,
}

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
