# Module 10 - Advanced Edition: Production Web Scraping

**Target**: Intermediate to Senior Developers
**Duration**: 8-12 hours
**Prerequisite**: Complete Beginner Edition

---

## 📚 What You'll Learn

### Lesson 1: Scrapy Framework
- Industrial-scale web scraping
- Building production spiders
- Item pipelines and middleware
- Error handling and deduplication
- **Time**: 2-3 hours

### Lesson 2: Celery + Redis
- Asynchronous task processing
- Background job scheduling
- Task monitoring and retries
- Distributed processing
- **Time**: 2-3 hours

### Lesson 3: Scrapy + Django Integration
- Running Scrapy from Django
- Storing data in Django ORM
- Duplicate detection
- Admin interface management
- **Time**: 2-3 hours

### Lesson 4: Production Patterns
- Redis caching strategies
- Rate limiting implementation
- Structured logging
- Error monitoring
- Database optimization
- Performance monitoring
- **Time**: 2-3 hours

---

## 📁 Project Structure

```
02_advanced_edition/
├── README.md                          # This file
├── QUICKSTART.md                      # 5-minute setup guide
│
├── theory/                            # Theoretical concepts (markdown + links)
│   ├── 01_scrapy_concepts.md
│   ├── 02_celery_architecture.md
│   ├── 03_integration_patterns.md
│   └── 04_production_patterns.md
│
├── code/                              # Practical, working code
│   ├── scrapy_project/                # Full Scrapy project
│   │   ├── scrapy.cfg
│   │   └── quotescrawler/
│   │       ├── settings.py
│   │       ├── items.py
│   │       ├── pipelines.py
│   │       ├── middlewares.py
│   │       └── spiders/
│   │           ├── quotes_spider.py
│   │           └── books_spider.py
│   │
│   ├── celery_tasks/                  # Celery task definitions
│   │   ├── __init__.py
│   │   ├── config.py                  # Celery configuration
│   │   └── tasks.py                   # Task definitions
│   │
│   ├── django_integration/            # Django management commands
│   │   ├── manage_commands/
│   │   │   └── scrape_quotes.py
│   │   ├── models.py                  # Django ORM models
│   │   └── views.py                   # Task triggering views
│   │
│   └── utils/                         # Shared utilities
│       ├── cache.py                   # Redis caching
│       ├── rate_limiter.py            # Rate limiting
│       ├── logging_config.py           # Structured logging
│       └── monitoring.py               # Performance monitoring
│
├── tutorials/                         # Step-by-step guides
│   ├── 01_scrapy_tutorial.md
│   ├── 02_celery_tutorial.md
│   ├── 03_integration_tutorial.md
│   └── 04_production_tutorial.md
│
└── examples/                          # Complete working examples
    ├── 01_scrape_and_store.py            # Full workflow example
    ├── 02_scheduled_scraping.py           # Celery Beat scheduler
    └── 03_production_app.py               # Production-ready application
```

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Navigate to module
cd /root/goit/python_web/module_10

# 2. Start services
docker-compose up -d

# 3. Verify Redis
docker-compose exec redis redis-cli ping
# Expected: PONG

# 4. Run first example
cd 02_advanced_edition/code
python scrapy_project/quotescrawler/spiders/quotes_spider.py

# 5. View results
# Check database or JSON output
```

For detailed setup: See [QUICKSTART.md](QUICKSTART.md)

---

## 🎯 Learning Path

### Phase 1: Understanding Scrapy (Day 1)
1. Read [Scrapy Concepts](theory/01_scrapy_concepts.md)
2. Follow [Scrapy Tutorial](tutorials/01_scrapy_tutorial.md)
3. Run working spiders in `code/scrapy_project/`
4. Experiment with pipelines and middleware

### Phase 2: Async Task Processing (Day 2)
1. Read [Celery Architecture](theory/02_celery_architecture.md)
2. Follow [Celery Tutorial](tutorials/02_celery_tutorial.md)
3. Write and test Celery tasks
4. Monitor with Flower dashboard

### Phase 3: Integration (Day 3)
1. Read [Integration Patterns](theory/03_integration_patterns.md)
2. Follow [Integration Tutorial](tutorials/03_integration_tutorial.md)
3. Create Django management commands
4. Build complete workflow

### Phase 4: Production (Day 4)
1. Read [Production Patterns](theory/04_production_patterns.md)
2. Follow [Production Tutorial](tutorials/04_production_tutorial.md)
3. Implement caching, rate limiting, monitoring
4. Deploy example application

---

## 💻 Code-First Learning

All code is:
- ✅ **Functional** - Works out of the box
- ✅ **Practical** - Real-world patterns
- ✅ **SOLID** - Proper design principles
- ✅ **DRY** - No duplication
- ✅ **Documented** - Docstrings and logging where appropriate
- ✅ **Tested** - Example data included

Run examples and spiders:
```bash
cd code/scrapy_project
scrapy crawl quotes

python examples/01_scrape_and_store.py
python examples/02_scheduled_scraping.py
```

---

## 📖 Theory-First Understanding

Theory is documented in separate markdown files with:
- **Concepts explained** - Architecture diagrams and patterns
- **Official documentation links** - To Django, Scrapy, Celery, Redis docs
- **Real-world use cases** - Why this matters
- **Best practices** - Production-ready patterns

Core modules avoid print-only explanations; example scripts may emit CLI output for demos.

---

## 🔧 Common Tasks

### Run a Scrapy Spider
```bash
cd code/scrapy_project
scrapy crawl quotes
scrapy crawl quotes -o quotes.json
```

### Start Celery Worker
```bash
# Terminal 1: Worker
celery -A celery_tasks worker --loglevel=info

# Terminal 2: Beat scheduler (optional)
celery -A celery_tasks beat --loglevel=info

# Terminal 3: Flower (monitoring at http://localhost:5555)
celery -A celery_tasks flower
```

### Trigger Scraping from Django
```bash
python manage.py scrape_quotes
# or programmatically
from celery_tasks.tasks import scrape_quotes_task
scrape_quotes_task.delay()
```

### View Cached Data
```bash
redis-cli
> get quote:1
> keys quote:*
> ttl quote:1
```

---

## 📊 Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Scrapy | 2.11 | Web scraping framework |
| Celery | 5.3 | Async task processing |
| Redis | 7 | Message broker + cache |
| Django | 5.0 | Web framework + ORM |
| PostgreSQL | 16 | Database |
| Python | 3.11+ | Language |

All included in `requirements.txt`

---

## 🎓 Success Criteria

After completing Advanced Edition, you should be able to:

**Scrapy**
- [ ] Build production spiders
- [ ] Implement custom pipelines
- [ ] Handle errors and retries
- [ ] Scrape JavaScript-heavy sites

**Celery**
- [ ] Configure task queues
- [ ] Write async tasks
- [ ] Monitor execution
- [ ] Schedule periodic jobs

**Integration**
- [ ] Run Scrapy from Django
- [ ] Store in ORM
- [ ] Handle duplicates
- [ ] Admin interface management

**Production**
- [ ] Implement caching
- [ ] Add rate limiting
- [ ] Structured logging
- [ ] Monitor performance

---

## 📈 Expected Results

With production patterns, you can:
- Scrape 100,000+ pages/hour
- Process 1,000+ async tasks/second
- Cache 99%+ of reads
- Handle 10,000+ requests/second

---

## 🆘 Troubleshooting

### Redis Connection Failed
```bash
docker-compose restart redis
redis-cli ping
```

### Celery Worker Not Starting
```bash
# Check if Redis running
redis-cli ping

# Check imports
python -c "from celery_tasks import config"
```

### Scrapy Spider Hangs
```bash
# Check for zombie processes
ps aux | grep scrapy

# Run with limited concurrency
scrapy crawl quotes -a CONCURRENT_REQUESTS=8
```

See [QUICKSTART.md](QUICKSTART.md) for more solutions.

---

## 📚 Additional Resources

### Official Documentation
- [Scrapy Docs](https://docs.scrapy.org/)
- [Celery Docs](https://docs.celeryproject.io/)
- [Django Docs](https://docs.djangoproject.com/)
- [Redis Docs](https://redis.io/documentation)

### Tools
- **Flower** - Celery task monitoring (web UI)
- **Redis Commander** - Redis data visualization
- **Scrapy Shell** - Interactive spider development

### Books & Guides
- "Web Scraping with Python" by Ryan Mitchell
- "Two Scoops of Django" by Greenfeld & Greenfeld
- Official Celery Best Practices guide

---

## 🎯 Next Steps After Advanced Edition

### Deploy to Production
- AWS/DigitalOcean deployment
- CI/CD pipelines
- Docker containers
- Monitoring dashboards

### Advanced Topics
- GraphQL APIs
- Real-time WebSockets
- Machine learning integration
- Advanced caching strategies

### Professional Development
- Performance optimization
- Cost reduction strategies
- Capacity planning
- On-call debugging

---

## ✅ Exercises

### Level 1 (Beginner)
- [ ] Run example spiders
- [ ] Modify spider output format
- [ ] Change scraping schedule
- [ ] View cached data

### Level 2 (Intermediate)
- [ ] Create new spider for different site
- [ ] Implement custom pipeline
- [ ] Write Celery task
- [ ] Build admin interface

### Level 3 (Advanced)
- [ ] Optimize spider performance
- [ ] Implement distributed caching
- [ ] Build monitoring dashboard
- [ ] Add error alerting

### Level 4 (Expert)
- [ ] Deploy to production server
- [ ] Set up auto-scaling
- [ ] Implement high availability
- [ ] Build complete system from scratch

---

## 📝 Notes

- **Theory first**: Read markdown files before diving into code
- **Code second**: Run working examples to understand patterns
- **Practice third**: Modify examples for your use cases
- **Troubleshoot**: Use QUICKSTART.md for common issues

All code is production-ready. No toy examples.

---

**Ready to build industrial-strength web scraping systems? Start with [Lesson 1: Scrapy Concepts](theory/01_scrapy_concepts.md)** 🚀
