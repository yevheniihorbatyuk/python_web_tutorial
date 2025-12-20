# Quick Start Guide - 5 Minutes

Get Advanced Edition up and running in 5 minutes.

---

## Prerequisites

✅ Beginner Edition completed
✅ Docker installed and running
✅ Python 3.11+
✅ Git cloned

---

## 1. Start Services (1 minute)

```bash
cd /root/goit/python_web/module_10

# Start PostgreSQL, Redis, pgAdmin
docker-compose up -d

# Verify Redis is running
docker-compose exec redis redis-cli ping
# Output: PONG
```

---

## 2. Run First Spider (2 minutes)

```bash
cd 02_advanced_edition/code/scrapy_project

# Scrape quotes
scrapy crawl quotes

# Watch output... you'll see quotes being extracted
# When done, check output:
cat data/quotes_output.jsonl | head -5
```

---

## 3. Check Database (1 minute)

```bash
# Access pgAdmin
# Go to http://localhost:5050
# Login: admin@admin.com / admin
# See PostgreSQL server: localhost:5432

# Or use command line
psql -U goit -d goit_module10
SELECT COUNT(*) FROM quotes;  # Will be 0 (not integrated yet)
```

---

## 4. View Redis Cache (1 minute)

```bash
# Check Redis data
redis-cli
> KEYS *
> GET quote:1
> FLUSHDB
> EXIT
```

---

## ✅ You're Ready!

Next steps:

1. **Understand**: Read [Scrapy Concepts](theory/01_scrapy_concepts.md)
2. **Practice**: Follow [Scrapy Tutorial](tutorials/01_scrapy_tutorial.md)
3. **Advance**: Move to [Lesson 2: Celery](theory/02_celery_architecture.md)

---

## Common Issues

### Port Already in Use

```bash
# If port 5432 (PostgreSQL) is busy
docker-compose down
docker-compose up -d
```

### Permission Denied

```bash
# If you get permission errors
sudo docker-compose up -d
```

### Spider Doesn't Run

```bash
# Check Scrapy installed
python -c "import scrapy; print(scrapy.__version__)"

# If missing
pip install scrapy
```

---

## What's Happening

```
1. Docker starts PostgreSQL, Redis, pgAdmin
2. You run: scrapy crawl quotes
3. Scrapy spider:
   - Fetches https://quotes.toscrape.com
   - Extracts quotes with CSS selectors
   - Validates data
   - Checks for duplicates
   - Saves to JSON file: data/quotes_output.jsonl
4. Data is ready for next steps (database, cache, etc.)
```

---

## File Locations

| What | Where |
|------|-------|
| Spiders | `code/scrapy_project/quotescrawler/spiders/` |
| Output | `code/scrapy_project/data/` |
| Theory | `theory/*.md` |
| Tutorials | `tutorials/*.md` |
| Examples | `examples/` |

---

Enjoy! 🚀
