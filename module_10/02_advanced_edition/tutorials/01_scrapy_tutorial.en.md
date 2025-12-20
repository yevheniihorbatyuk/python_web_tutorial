# Tutorial: Getting Started with Scrapy

**Goal**: Build and run your first Scrapy spider.

---

## Setup

1.  **Navigate to the Scrapy project directory**:
    ```bash
    cd /root/goit/python_web/module_10/02_advanced_edition/code/scrapy_project
    ```
2.  **Verify the project structure**: You should see a `scrapy.cfg` file and a `quotescrawler` directory.

---

## Step 1: Run Your First Spider

Scrapy commands are run from the project's root directory.

### 1a. Crawl the Spider

The `crawl` command runs a spider.
```bash
scrapy crawl quotes
```
You will see logs of the spider fetching pages and extracting data.

### 1b. Save Output to a File

You can save the scraped data directly to a file (e.g., JSON, CSV).
```bash
scrapy crawl quotes -o quotes.json
```
This will create a `quotes.json` file with the results.

---

## Step 2: Understanding the Spider Code

Open `quotescrawler/spiders/quotes_spider.py`.

```python
class QuotesSpider(scrapy.Spider):
    # A unique name for the spider
    name = 'quotes'
    # The domains this spider is allowed to crawl
    allowed_domains = ['quotes.toscrape.com']
    # The URL(s) where the spider will begin to crawl
    start_urls = ['https://quotes.toscrape.com/']

    def parse(self, response):
        """
        This method is called to handle the response downloaded for each
        of the requests made.
        """
        # Loop through each quote element on the page
        for quote_div in response.css('div.quote'):
            # Yield a dictionary with the extracted data
            yield {
                'text': quote_div.css('span.text::text').get(),
                'author': quote_div.css('small.author::text').get(),
            }

        # Find the link to the next page and follow it
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
```
- **`yield`**: In Scrapy, `yield` is used to return extracted data or to return new requests to follow.

---

## Step 3: Interactive Testing with Scrapy Shell

The `shell` is an interactive console that lets you test your selectors on a live page.

1.  **Launch the shell**:
    ```bash
    scrapy shell 'https://quotes.toscrape.com'
    ```
2.  **Test your selectors**: Inside the shell, you have access to the `response` object.
    ```python
    # Get the title of the page
    >>> response.css('title::text').get()
    'Quotes to Scrape'

    # Get the text of the first quote
    >>> response.css('div.quote span.text::text').get()
    '"The world as we have created it is a process of our thinking..."'
    ```

This is the best way to figure out the correct selectors before writing your spider.
