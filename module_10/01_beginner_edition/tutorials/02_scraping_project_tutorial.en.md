# Tutorial: Building a Robust Scraper

This tutorial demonstrates how to build a more advanced scraper using the concepts from the theory lesson. We will use the code in `code/02_real_world_scraping.py` as our reference.

**Goal:** Scrape quotes, handle errors, and save the data to an SQLite database.

---

## Step 1: Understand the Code Structure

Open `code/02_real_world_scraping.py`. It contains three main classes:
- **`Article`**: A `dataclass` to hold the scraped data.
- **`ArticleDatabase`**: Manages all interactions with the SQLite database.
- **`RobustScraper`**: The main scraper class, which includes retry logic.

---

## Step 2: Running the Scraper

The script is designed to be run directly. Open your terminal and execute:
```bash
python 01_beginner_edition/code/02_real_world_scraping.py
```

### What Happens When You Run It?

1.  The `main_workflow()` function is called.
2.  An instance of `RobustScraper` is created.
3.  The scraper fetches HTML from `quotes.toscrape.com`, automatically retrying on failure.
4.  It parses the quotes and stores them as `Article` objects.
5.  An instance of `ArticleDatabase` is created, which also creates an `articles.db` file if it doesn't exist.
6.  The scraped articles are saved to the database. Duplicates (based on URL) are automatically skipped.
7.  The script logs its progress to the console.

---

## Step 3: Key Code Explained

### The `_fetch_with_retry` Method

This is the core of the robust scraper. It wraps `requests.get()` in a loop.

```python
# Inside the RobustScraper class
def _fetch_with_retry(self, url: str) -> Optional[str]:
    for attempt in range(self.max_retries):
        try:
            # ... requests.get(url) ...
            return response.text
        except requests.RequestException as e:
            log.warning(f"Attempt {attempt + 1} failed.")
            if attempt < self.max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                log.error("Failed after all retries.")
                return None
```

### The `ArticleDatabase` Class

This class handles all database logic, keeping it separate from the scraping code.

```python
# Inside the ArticleDatabase class
def save_articles(self, articles: List[Article]) -> int:
    saved_count = 0
    cursor = self.conn.cursor()
    for article in articles:
        try:
            # The UNIQUE constraint on the 'url' column prevents duplicates
            cursor.execute("INSERT INTO ...", (...))
            saved_count += 1
        except sqlite3.IntegrityError:
            # This error is expected if the URL already exists
            log.warning(f"Article with URL {article.url} already exists.")
    
    self.conn.commit()
    return saved_count
```

---

## Step 4: Verifying the Output

After running the script, you will find a new file named `articles.db` in the project directory. This is your SQLite database.

You can inspect it using a database tool like [DB Browser for SQLite](https://sqlitebrowser.org/), or directly from the command line:

```bash
# Install the SQLite command-line tool if you don't have it
# (On Ubuntu: sudo apt-get install sqlite3)

# Open the database
sqlite3 articles.db

# Run some SQL queries
sqlite> .tables
articles

sqlite> SELECT COUNT(*) FROM articles;
30

sqlite> SELECT author, title FROM articles LIMIT 3;
Albert Einstein|"The world as we have created it is a process of our thinking..."
J.K. Rowling|"It is our choices, Harry, that show what we truly are, far more than our abilities."
Albert Einstein|"There are only two ways to live your life. One is as though nothing is a miracle..."

sqlite> .quit
```

Each time you run the script, it will only add new articles if it finds any, thanks to the `UNIQUE` constraint on the URL.
