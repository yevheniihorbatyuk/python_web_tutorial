# Lesson 2: Real-World Scraping Project

## Introduction: Building Production-Ready Scrapers

Lesson 1 covered the basics. Now, we'll build a production-grade scraper that includes:
- Robust error handling and retries.
- Data validation and cleaning.
- Persistence to a database.
- Professional logging.

## The Complete Workflow

A real-world scraping process looks like this:
1.  **Fetch Data** (with retry logic for network failures).
2.  **Parse HTML** into a structured format.
3.  **Extract Items** into data models.
4.  **Validate Data** to ensure quality.
5.  **Check for Duplicates** to avoid redundant entries.
6.  **Store in a Database** for persistence and querying.
7.  **Log Everything** for monitoring and debugging.

---

## Part 1: Key Concepts for Robust Scraping

### Retry Logic (Exponential Backoff)

Networks are unreliable. When a request fails, don't give up immediately. **Exponential backoff** is a strategy where you retry a failed request with progressively longer wait times.

**Pattern:**
- Attempt 1: Fails. Wait 1 second.
- Attempt 2: Fails. Wait 2 seconds.
- Attempt 3: Fails. Wait 4 seconds.

This gives temporary network or server issues time to resolve.

### Structured Data with Dataclasses

Instead of plain dictionaries, use Python's `dataclasses` to define a clear structure for your data.

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Article:
    title: str
    url: str
    author: str
    scraped_at: str = field(default_factory=datetime.now().isoformat)
```
**Benefits:** Type hints, default values, and self-documenting code.

### Logging (Not `print()`)

In production, `print()` is not enough. The `logging` module provides:
- **Severity Levels:** `INFO`, `WARNING`, `ERROR`.
- **Timestamps:** Know *when* something happened.
- **Configurability:** Output to console, files, or external services.

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

logging.info("Scraping started.")
logging.error("Failed to fetch page.")
```

### Database Persistence with SQLite

For storing scraped data, a database is more reliable than a simple file. **SQLite** is a lightweight, file-based database that's built into Python.

**Key Operations:**
- **`CREATE TABLE`**: Define the schema (columns and data types).
- **`INSERT`**: Add new records.
- **`UNIQUE` constraint**: Prevent duplicate entries based on a specific field (like a URL).

---
## Additional Resources

- [Python `dataclasses` Documentation](https://docs.python.org/3/library/dataclasses.html)
- [Python `logging` HOWTO](https://docs.python.org/3/howto/logging.html)
- [Python `sqlite3` Module Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Requests: Advanced Usage (Retries)](https://requests.readthedocs.io/en/latest/user/advanced/)
