# Lesson 1: Scrapy Framework Concepts

**Goal**: Understand Scrapy architecture and when to use it.
**Prerequisites**: BeautifulSoup basics from Beginner Edition

---

## What is Scrapy?

Scrapy is a **Python framework for large-scale web scraping and web crawling**. Unlike BeautifulSoup (which is just an HTML parser), Scrapy is a complete framework that handles:

- **Request management** - concurrent requests, retries, throttling
- **HTML parsing** - with CSS/XPath selectors
- **Data extraction** - structured data pipelines
- **Persistence** - saving to databases, files, APIs
- **Scheduling** - periodic crawling
- **Monitoring** - request/response statistics

### When to Use Scrapy

| Use Scrapy | Use BeautifulSoup |
|-----------|------------------|
| 100,000+ pages to scrape | < 1,000 pages |
| Need concurrency | Single-threaded OK |
| Complex pipelines | Simple HTML parsing |
| Long-running crawls | One-off scripts |
| Production systems | Learning/experimentation |

---

## Architecture Overview

Scrapy follows a **Pipeline Pattern** where data flows through components:

```
┌─────────────────────────────────────────────────────────┐
│                    SCRAPY ENGINE                        │
│  (Coordinator: manages all other components)            │
└──────────────┬──────────────────┬──────────────────────┘
               │                  │
               ↓                  ↓
      ┌────────────────┐  ┌──────────────────┐
      │  SCHEDULER     │  │  DOWNLOADER      │
      │                │  │                  │
      │ Manages queue  │  │ Fetches pages    │
      │ of URLs        │  │ over HTTP        │
      └────────┬───────┘  └────────┬─────────┘
               │                   │
               ↓                   ↓
      ┌────────────────────────────────────┐
      │         SPIDER                      │
      │                                    │
      │ Parses HTML, extracts data         │
      │ Yields items and new URLs          │
      └────────────────┬───────────────────┘
                       │
                       ↓
      ┌────────────────────────────────────┐
      │      ITEM PIPELINES                │
      │                                    │
      │ 1. ValidationPipeline              │
      │ 2. DuplicateFilterPipeline         │
      │ 3. DatabasePipeline                │
      │ 4. JsonExportPipeline              │
      └────────────────────────────────────┘
```

### Key Components

- **Engine**: Central coordinator that manages the data flow.
- **Scheduler**: Maintains the queue of URLs to crawl.
- **Downloader**: Fetches web pages.
- **Spider**: Your custom code that parses HTML and extracts data.
- **Item Pipelines**: Process the extracted data (validation, cleaning, saving).

---

## Data Extraction

Scrapy uses **CSS Selectors** and **XPath** for extraction:

### CSS Selectors (Easier)

```python
response.css('div.quote')        # <div class="quote">
response.css('a::attr(href)')    # href attribute
response.css('h1::text')         # Text content
```

### XPath (More Powerful)

```python
response.xpath('//div[@class="quote"]')
response.xpath('//h1/text()')
```

---
## Additional Resources

- **Scrapy Tutorial**: https://docs.scrapy.org/en/latest/intro/tutorial.html
- **Scrapy Architecture**: https://docs.scrapy.org/en/latest/topics/architecture.html
