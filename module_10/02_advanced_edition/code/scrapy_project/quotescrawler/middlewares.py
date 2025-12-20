"""Scrapy middleware for quotescrawler"""

import logging
import random
import time
from typing import Optional


class UserAgentMiddleware:
    """Rotate User-Agent headers to avoid blocking"""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
    ]

    def process_request(self, request, spider):
        """Set random User-Agent"""
        request.headers['User-Agent'] = random.choice(self.USER_AGENTS)


class RateLimitMiddleware:
    """Rate limiting middleware to be polite to servers"""

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)
        self.last_request_time = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        """Add delay between requests to same domain"""
        domain = request.url.split('/')[2]
        min_delay = spider.settings.getfloat('DOWNLOAD_DELAY', 1)

        if domain in self.last_request_time:
            time_since_last = time.time() - self.last_request_time[domain]
            if time_since_last < min_delay:
                sleep_time = min_delay - time_since_last
                self.logger.debug(f'Rate limiting: sleeping {sleep_time:.2f}s')
                time.sleep(sleep_time)

        self.last_request_time[domain] = time.time()

    def process_response(self, request, response, spider):
        """Handle rate limiting responses (429 Too Many Requests)"""
        if response.status == 429:
            self.logger.warning(f'Got 429 from {request.url}, backing off')
            # Increase delay for this domain
            domain = request.url.split('/')[2]
            current_delay = spider.settings.getfloat('DOWNLOAD_DELAY', 1)
            spider.settings.set('DOWNLOAD_DELAY', current_delay * 1.5)

        return response
