"""
Lesson 1: Practical Web Scraping with Beautiful Soup

This script provides a complete, production-ready example of web scraping
using the Beautiful Soup and Requests libraries. It demonstrates:
- Fetching HTML from a live website.
- Parsing the HTML to extract structured data.
- Handling potential errors gracefully (e.g., network issues, missing data).
- Implementing politeness with delays to avoid overloading the server.
- Storing the extracted data in a clean JSON format.

The code is structured using classes and adheres to DRY and SOLID principles.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

# --- Configuration ---
# It's good practice to keep settings at the top.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# Using a logger object is better than print() for production code.
log = logging.getLogger(__name__)

# --- Reusable Fetching Utility ---

def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetches HTML content from a URL with a browser-like user-agent.

    Args:
        url: The URL of the website to fetch.
        timeout: The number of seconds to wait for a response.

    Returns:
        The HTML content as a string, or None if an error occurs.
    """
    # A User-Agent header makes the request look like it's from a real browser,
    # which is necessary for many websites.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        # This will raise an exception for HTTP error codes (4xx or 5xx).
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        log.error(f"Error fetching URL {url}: {e}")
        return None

# --- Main Scraper Class ---

class QuoteScraper:
    """
    A scraper designed to extract quotes from quotes.toscrape.com.
    
    This class encapsulates all the logic for scraping, parsing, and storing quotes.
    """
    BASE_URL = "http://quotes.toscrape.com"

    def __init__(self):
        self.quotes: List[Dict] = []

    def _parse_quote(self, quote_tag: Tag) -> Optional[Dict]:
        """
        Parses a single quote <div> tag to extract its data.
        
        This is a private helper method to keep the main scraping logic clean.
        """
        try:
            text = quote_tag.find('span', class_='text').get_text(strip=True)
            author = quote_tag.find('small', class_='author').get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote_tag.find_all('a', class_='tag')]

            return {
                'text': text,
                'author': author,
                'tags': tags,
                'scraped_at': datetime.now().isoformat()
            }
        except AttributeError as e:
            # This error happens if the HTML structure is not as expected.
            log.warning(f"Could not parse a quote, HTML structure might have changed. Details: {e}")
            return None

    def scrape_site(self, max_pages: int = 5) -> None:
        """
        Scrapes the website page by page until no more pages are found or max_pages is reached.

        Args:
            max_pages: The maximum number of pages to scrape.
        """
        log.info(f"Starting scrape of {self.BASE_URL}")
        for page_num in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/page/{page_num}/"
            log.info(f"Scraping page {page_num}: {url}")

            html = fetch_html(url)
            if not html:
                log.warning(f"Failed to fetch page {page_num}, stopping scrape.")
                break

            soup = BeautifulSoup(html, 'html.parser')
            
            # The presence of the "Next" button link indicates if there are more pages.
            next_button = soup.find('li', class_='next')
            
            quote_tags = soup.find_all('div', class_='quote')
            if not quote_tags:
                log.info("No quotes found on this page, assuming it's the end.")
                break

            for quote_tag in quote_tags:
                quote_data = self._parse_quote(quote_tag)
                if quote_data:
                    self.quotes.append(quote_data)
            
            log.info(f"Found {len(quote_tags)} quotes on page {page_num}. Total quotes: {len(self.quotes)}")

            if not next_button:
                log.info("No 'Next' button found. This is the last page.")
                break
            
            # A delay is crucial to be respectful to the website's server.
            time.sleep(1)
        
        log.info(f"Scraping finished. Total quotes collected: {len(self.quotes)}")

    def save_to_json(self, filename: str = "quotes.json") -> None:
        """
        Saves the collected quotes to a JSON file.
        """
        if not self.quotes:
            log.warning("No quotes to save. Aborting JSON save.")
            return
            
        log.info(f"Saving {len(self.quotes)} quotes to {filename}...")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # `indent=2` makes the JSON file human-readable.
                # `ensure_ascii=False` is important for non-English characters.
                json.dump(self.quotes, f, indent=2, ensure_ascii=False)
            log.info(f"Successfully saved quotes to {filename}")
        except IOError as e:
            log.error(f"Failed to write to file {filename}: {e}")

# --- Main Execution Block ---

if __name__ == "__main__":
    """
    This block runs when the script is executed directly.
    It creates an instance of the scraper, runs the scraping process,
    and saves the results.
    """
    scraper = QuoteScraper()
    
    # We can control how many pages to scrape. Let's do 3 for this example.
    scraper.scrape_site(max_pages=3)
    
    # Save the results.
    scraper.save_to_json("scraped_quotes.json")

    # You can optionally print a few results to verify.
    if scraper.quotes:
        log.info("--- First 3 Scraped Quotes ---")
        for quote in scraper.quotes[:3]:
            log.info(f"'{quote['text']}' - {quote['author']}")
        log.info("-----------------------------")

    log.info("Script finished.")