# Advanced Edition - Complete Index

## 📚 Start Here

**New to this module?** Start with one of these:
1. [QUICKSTART.md](QUICKSTART.md) - 5-minute setup (⏱️ 5 min)
2. [README.md](README.md) - Complete guide (📖 15 min)
3. [STRUCTURE.md](STRUCTURE.md) - How it's organized (📐 10 min)

---

## 🎓 Learning Path

### Phase 1: Theory (Read to understand concepts)

| # | Lesson | File | Duration | Topics |
|---|--------|------|----------|--------|
| 1 | Scrapy Framework | [theory/01_scrapy_concepts.md](theory/01_scrapy_concepts.md) | 30 min | Architecture, spiders, pipelines, middleware |
| 2 | Celery + Redis | [theory/02_celery_architecture.md](theory/02_celery_architecture.md) | 25 min | Task queues, workers, scheduling, retries |
| 3 | Integration | [theory/03_integration_patterns.md](theory/03_integration_patterns.md) | 30 min | Django ORM, management commands, data flow |
| 4 | Production | [theory/04_production_patterns.md](theory/04_production_patterns.md) | 30 min | Caching, rate limiting, logging, monitoring |

**Total**: ~2 hours of reading

### Phase 2: Tutorials (Follow along step-by-step)

| # | Lesson | File | Duration | Topics |
|---|--------|------|----------|--------|
| 1 | Scrapy Hands-On | [tutorials/01_scrapy_tutorial.md](tutorials/01_scrapy_tutorial.md) | 45 min | Run spider, modify, extract data |
| 2 | Celery Hands-On | [tutorials/02_celery_tutorial.md](tutorials/02_celery_tutorial.md) | 45 min | Start worker, submit tasks, monitor |
| 3 | Integration Hands-On | [tutorials/03_integration_tutorial.md](tutorials/03_integration_tutorial.md) | 45 min | Complete workflow from Django to ORM |
| 4 | Production Hands-On | [tutorials/04_production_tutorial.md](tutorials/04_production_tutorial.md) | 45 min | Caching, rate limiting, health checks |

**Total**: ~3 hours of hands-on practice

### Phase 3: Examples (See real implementations)

| # | Example | File | Duration | Use Case |
|---|---------|------|----------|----------|
| 1 | Scrape & Store | [examples/01_scrape_and_store.py](examples/01_scrape_and_store.py) | 20 min | Complete workflow with analysis |
| 2 | Scheduled Scraping | [examples/02_scheduled_scraping.py](examples/02_scheduled_scraping.py) | 20 min | Celery Beat setup and monitoring |
| 3 | Production API | [examples/03_production_app.py](examples/03_production_app.py) | 20 min | REST API with all patterns |

**Total**: ~1 hour of examples

---

## 💻 Production Code

### Scrapy Project

**Directory**: `code/scrapy_project/quotescrawler/`

| File | Lines | Purpose |
|------|-------|---------|
| [settings.py](code/scrapy_project/quotescrawler/settings.py) | 60 | Scrapy configuration |
| [items.py](code/scrapy_project/quotescrawler/items.py) | 15 | Data structures |
| [pipelines.py](code/scrapy_project/quotescrawler/pipelines.py) | 150 | Processing pipelines (validate, dedupe, export) |
| [middlewares.py](code/scrapy_project/quotescrawler/middlewares.py) | 90 | User-Agent rotation, rate limiting |
| [spiders/quotes_spider.py](code/scrapy_project/quotescrawler/spiders/quotes_spider.py) | 60 | Quotes spider |
| [spiders/books_spider.py](code/scrapy_project/quotescrawler/spiders/books_spider.py) | 70 | Books spider |

**Use**: `cd code/scrapy_project && scrapy crawl quotes`

### Celery Tasks

**Directory**: `code/celery_tasks/`

| File | Lines | Tasks |
|------|-------|-------|
| [config.py](code/celery_tasks/config.py) | 80 | Celery app configuration, Beat schedule |
| [tasks.py](code/celery_tasks/tasks.py) | 300+ | 11 production tasks with retries, progress tracking |

**Use**: `celery -A code.celery_tasks worker --loglevel=info`

### Django Integration

**Directory**: `code/django_integration/`

| File | Lines | Contents |
|------|-------|----------|
| [models.py](code/django_integration/models.py) | 250+ | 4 models: ScrapeJob, Quote, Book, ScrapingSchedule |
| [views.py](code/django_integration/views.py) | 150+ | 3 API views for scraping control |

**Use**: `python manage.py migrate && python manage.py runserver`

### Utilities

**Directory**: `code/utils/`

| File | Lines | Features |
|------|-------|----------|
| [cache.py](code/utils/cache.py) | 200+ | CacheManager (Cache-Aside, Write-Through), QuoteCache, BookCache |
| [rate_limiter.py](code/utils/rate_limiter.py) | 200+ | 5 rate limiting algorithms, API limiter |

**Use**: `from code.utils.cache import CacheManager`

---

## 📋 Quick Reference

### Commands

```bash
# Setup
python manage.py migrate
python manage.py runserver

# Run Spider
cd code/scrapy_project
scrapy crawl quotes

# Celery
celery -A code.celery_tasks worker --loglevel=info
celery -A code.celery_tasks beat --loglevel=info
celery -A code.celery_tasks flower --port=5555

# Examples
python examples/01_scrape_and_store.py scrape
python examples/02_scheduled_scraping.py setup
python examples/03_production_app.py demo

# Logs
tail -f logs/scraping.log
```

### APIs

```bash
# Get quotes
curl http://localhost:8000/api/quotes/?page=1&page_size=20

# Get single quote
curl http://localhost:8000/api/quotes/1/

# Statistics
curl http://localhost:8000/api/stats/

# Health check
curl http://localhost:8000/api/health/

# Start scraping
curl -X POST http://localhost:8000/api/scrape/start/

# Job status
curl http://localhost:8000/api/scrape/<task_id>/
```

---

## 🎯 Learning Outcomes

After completing all phases, you can:

### Knowledge
- ✅ Understand Scrapy architecture and request/response cycle
- ✅ Design task queues with Celery + Redis
- ✅ Implement production caching strategies
- ✅ Apply rate limiting algorithms
- ✅ Build monitoring systems
- ✅ Optimize database queries

### Skills
- ✅ Build custom spiders for any website
- ✅ Create Celery tasks with error handling
- ✅ Integrate Scrapy with Django ORM
- ✅ Implement REST APIs with caching
- ✅ Monitor systems with Flower
- ✅ Debug and optimize performance

### Systems
- ✅ Single-machine web scraper
- ✅ Scheduled scraping system
- ✅ Production REST API
- ✅ Database with proper indexing
- ✅ Caching layer with Redis
- ✅ Rate limiting for protection

---

## 🏗️ Project Structure

```
02_advanced_edition/
│
├── README.md                    ← Start here
├── QUICKSTART.md               ← 5-minute setup
├── STRUCTURE.md                ← Architecture
├── COMPLETION_SUMMARY.md       ← What was built
├── INDEX.md                    ← This file
│
├── theory/                     ← Read these
│   ├── 01_scrapy_concepts.md
│   ├── 02_celery_architecture.md
│   ├── 03_integration_patterns.md
│   └── 04_production_patterns.md
│
├── tutorials/                  ← Follow these
│   ├── 01_scrapy_tutorial.md
│   ├── 02_celery_tutorial.md
│   ├── 03_integration_tutorial.md
│   └── 04_production_tutorial.md
│
├── examples/                   ← Run these
│   ├── 01_scrape_and_store.py
│   ├── 02_scheduled_scraping.py
│   └── 03_production_app.py
│
├── code/                       ← Production code
│   ├── scrapy_project/
│   ├── celery_tasks/
│   ├── django_integration/
│   └── utils/
│
└── logs/                       ← Generated logs
    ├── app.log
    └── scraping.log
```

---

## 🚀 Quick Start Commands

```bash
# 1. Setup (one-time)
cd /root/goit/python_web/module_10/02_advanced_edition

# 2. Read
cat QUICKSTART.md  # 5 minutes

# 3. Run
python manage.py runserver              # Terminal 1
celery -A code.celery_tasks worker      # Terminal 2
celery -A code.celery_tasks flower      # Terminal 3 (optional)

# 4. Test
curl http://localhost:8000/api/quotes/

# 5. Learn
python examples/01_scrape_and_store.py scrape
```

---

## ❓ FAQ

**Q: Where do I start?**
A: Start with [QUICKSTART.md](QUICKSTART.md) (5 min) then [README.md](README.md) (15 min)

**Q: How long does it take?**
A: 4-6 hours for the complete learning path (2h theory + 3h tutorials + 1h examples)

**Q: Do I need Docker?**
A: Recommended but not required. See [QUICKSTART.md](QUICKSTART.md) for setup options.

**Q: Where's the database?**
A: PostgreSQL in docker-compose.yml (or use SQLite for development)

**Q: How do I run the examples?**
A: `python examples/01_scrape_and_store.py` (requires Django setup)

**Q: What if something breaks?**
A: Check the troubleshooting section in each tutorial or see [README.md](README.md#troubleshooting)

---

## 📞 Support

- **Questions about theory?** See the theory/\*.md files with links to official docs
- **Can't get something working?** Check troubleshooting in the relevant tutorial
- **Want to understand the architecture?** Read [STRUCTURE.md](STRUCTURE.md)
- **Looking for code examples?** See examples/\*.py

---

## ✅ Completion Checklist

Use this to track your progress:

- [ ] Read [QUICKSTART.md](QUICKSTART.md)
- [ ] Read [README.md](README.md)
- [ ] Read all 4 theory files (~/2 hours)
- [ ] Follow all 4 tutorials (~/3 hours)
  - [ ] Tutorial 1: Scrapy (45 min)
  - [ ] Tutorial 2: Celery (45 min)
  - [ ] Tutorial 3: Integration (45 min)
  - [ ] Tutorial 4: Production (45 min)
- [ ] Run example 1 (20 min)
- [ ] Run example 2 (20 min)
- [ ] Run example 3 (20 min)
- [ ] **Total: 4-6 hours**

---

## 🎓 Certificate of Completion

After completing all phases, you understand:
- ✅ Production web scraping architecture
- ✅ Async task processing patterns
- ✅ Database integration strategies
- ✅ Caching and optimization
- ✅ Monitoring and debugging
- ✅ Real-world deployment

**You're ready to build production web scraping systems!** 🚀

---

**Last Updated**: 2024
**Module Status**: ✅ Complete (8,898 lines, 30 files)
**Ready for**: Production use, team training, personal projects

---

**Next Steps**:
1. Try the examples
2. Build your own spider
3. Deploy to your infrastructure
4. Monitor and optimize
5. Share what you build!
