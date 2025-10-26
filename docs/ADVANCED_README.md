# 🚀 Advanced Modules - Production DS/DE Patterns

## Для Senior Data Scientists & Data Engineers

Це розширення базового курсу з **реальними production паттернами** та **modern best practices** для Data Science та Data Engineering.

---

## 🎯 Що Нового?

### Базовий Модуль (для всіх)
- ✅ Async basics та Event Loop
- ✅ HTTP запити з aiohttp
- ✅ SQL: SELECT, JOIN, GROUP BY
- ✅ Python + PostgreSQL basics
- ✅ Jupyter data analysis

### Advanced Модуль (для Senior DS/DE)
- 🚀 **Production ETL Pipeline** з async processing
- 🏗️ **Architectural Patterns** (Repository, DI, Factory)
- 🤖 **ML Feature Store** pattern
- 📊 **Advanced SQL Analytics** (Cohort, Funnel, Time-series)
- 📈 **Real-world Use Cases** з практичними прикладами

---

## 📁 Структура Advanced Modules

```
advanced_examples/
│
├── etl/
│   └── 01_async_etl_pipeline.py       # Production ETL з metrics
│
├── patterns/
│   └── 02_repository_pattern.py       # Clean Architecture patterns
│
├── ml_pipeline/
│   └── 03_feature_store.py            # ML infrastructure
│
└── monitoring/
    └── (coming soon: Prometheus metrics)

sql_examples/
└── 05_advanced_analytics.sql          # DS/DE SQL patterns
```

---

## 🔥 Module 1: Async ETL Pipeline

**Файл**: [advanced_examples/etl/01_async_etl_pipeline.py](advanced_examples/etl/01_async_etl_pipeline.py)

### Що Inside?

**Real-world ETL patterns**:
- ✅ Async extraction з множинних джерел (Weather API, Stock API)
- ✅ Type-safe data models з `@dataclass`
- ✅ Data validation та error handling
- ✅ Batch loading з UPSERT (conflict resolution)
- ✅ Metrics collection (Prometheus-style)
- ✅ Parallel pipeline execution

**Production Extensions discussed**:
- Retry logic з exponential backoff
- Circuit breaker для external APIs
- Dead letter queue для failed records
- Distributed tracing (OpenTelemetry)

### Use Cases
```python
# Weather + Stock data pipeline
pipeline = ETLPipeline()

# Паралельне виконання
await pipeline.run_parallel_pipelines(
    cities=['Kyiv', 'Lviv', 'Odesa'],
    symbols=['AAPL', 'GOOGL', 'MSFT']
)

# Metrics tracking
pipeline.metrics.print_summary()
# Output:
#   records_extracted: 10
#   records_transformed: 10
#   records_loaded: 10
#   errors: 0
#   duration_seconds: 1.2
```

### Запуск
```bash
python advanced_examples/etl/01_async_etl_pipeline.py
```

---

## 🏗️ Module 2: Architectural Patterns

**Файл**: [advanced_examples/patterns/02_repository_pattern.py](advanced_examples/patterns/02_repository_pattern.py)

### Patterns Demonstrated

**1. Repository Pattern**
- Абстракція data access layer
- Легко змінювати БД (PostgreSQL → BigQuery)
- Interface segregation

**2. Dependency Injection**
- Loose coupling між компонентами
- Easy testing з mock implementations
- Clean dependency management

**3. Factory Pattern**
- Flexible object creation
- Configuration-based switching

**4. Service Layer**
- Business logic separation
- Domain-driven design

### Why це Важливо?

```python
# ❌ БЕЗ patterns - hard to test, tightly coupled
def register_customer(name, email):
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers ...")
    # SQL всюди, важко тестувати

# ✅ З patterns - clean, testable, flexible
class CustomerService:
    def __init__(self, repository: ICustomerRepository):
        self.repository = repository  # DI!

    def register_customer(self, name, email):
        # Business logic
        customer = Customer(name=name, email=email)
        return self.repository.add(customer)

# Testing:
service = CustomerService(InMemoryRepository())  # Mock!
service.register_customer("Test", "test@test.com")
```

### Real Benefits
- 🧪 **Testing**: Mock repositories для unit tests
- 🔄 **Flexibility**: Легко замінити PostgreSQL на MongoDB
- 📖 **Readability**: Clean separation of concerns
- 🏢 **Enterprise**: SOLID principles, scalable architecture

### Запуск
```bash
python advanced_examples/patterns/02_repository_pattern.py
```

---

## 🤖 Module 3: Feature Store for ML

**Файл**: [advanced_examples/ml_pipeline/03_feature_store.py](advanced_examples/ml_pipeline/03_feature_store.py)

### ML Infrastructure Pattern

**Problem**: В production ML, features часто:
- Compute у різних місцях (inconsistency)
- Re-computed для кожного model (waste)
- Training/serving skew (different code paths)

**Solution**: **Feature Store**
- Centralized feature repository
- Offline features (training) + Online features (serving)
- Feature versioning та lineage

### Architecture

```
┌─────────────┐
│ Raw Data    │
│ (PostgreSQL)│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Feature         │  ← Feature Engineering
│ Engineering     │     (Pandas/Spark)
└──────┬──────────┘
       │
       ├─────────────────┐
       ▼                 ▼
┌──────────────┐  ┌─────────────┐
│ Offline      │  │ Online      │
│ Store        │  │ Store       │
│ (PostgreSQL) │  │ (Redis)     │
└──────┬───────┘  └──────┬──────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌─────────────┐
│ ML Training  │  │ ML Serving  │
│              │  │ (Real-time) │
└──────────────┘  └─────────────┘
```

### Example Usage

```python
# 1. Initialize Feature Store
fs = FeatureStore(connection_string)

# 2. Compute features (scheduled job)
customer_features = fs.compute_customer_features()
# → Computes RFM, CLV, churn risk, segment

# 3. Save to offline store (batch)
fs.save_features("customer", customer_features)

# 4. Get features for training (offline)
training_data = fs.get_training_dataset(
    entity_type="customer",
    feature_names=['recency_days', 'frequency', 'monetary_value']
)

# 5. Get features for serving (online)
features = fs.get_features("customer", [1, 2, 3])
# → Fast lookup для real-time predictions
```

### Features Computed

**Customer Features**:
- RFM (Recency, Frequency, Monetary)
- Customer Lifetime Value
- Churn Risk Score
- Customer Segment
- Behavioral metrics

**Product Features**:
- Sales metrics
- Price features
- Popularity scores
- Time-series features

### Production Tools
- **Feast** - Open-source feature store
- **Tecton** - Managed platform
- **AWS SageMaker Feature Store**
- **Databricks Feature Store**

### Запуск
```bash
python advanced_examples/ml_pipeline/03_feature_store.py
```

---

## 📊 Module 4: Advanced SQL Analytics

**Файл**: [sql_examples/05_advanced_analytics.sql](sql_examples/05_advanced_analytics.sql)

### Що Inside?

**1. Time-Series Analysis**
```sql
-- Moving averages для згладжування
SELECT
    date,
    revenue,
    AVG(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as ma_7day
FROM daily_sales;
```

**2. Cohort Analysis**
```sql
-- Retention rate по cohorts
-- Показує як різні cohorts користувачів ведуть себе
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', registration_date) as cohort_month
    FROM customers
)
-- ... complex cohort logic
```

**3. Funnel Analysis**
```sql
-- Conversion funnel: Registration → Order → Repeat
-- Скільки % users проходять кожен step
```

**4. RFM Segmentation**
```sql
-- Advanced RFM з NTILE та сегментацією
-- Champions, Loyal, At Risk, Lost, etc.
```

**5. Product Affinity (Market Basket)**
```sql
-- Які товари купують разом?
-- Lift metric для recommendations
```

**6. ABC Analysis (Pareto)**
```sql
-- Класифікація товарів: A (80% revenue), B, C
```

**7. Statistical Functions**
```sql
-- Percentiles, outlier detection (IQR method)
-- Correlation analysis
```

**8. ML Feature Engineering**
```sql
-- Time-series features: lags, rolling stats
-- Churn prediction features
-- Date features для forecasting
```

### Use Cases

**Data Scientist**:
- Feature extraction для ML models
- Exploratory data analysis
- A/B test analysis
- Cohort та retention analysis

**Data Engineer**:
- dbt models для data transformation
- Airflow SQL tasks
- Data quality checks
- Metric computation

**Analytics Engineer**:
- Business metrics
- Dashboard queries
- KPI tracking
- Segment analysis

### Запуск
```bash
# В psql або pgAdmin
\i sql_examples/05_advanced_analytics.sql

# Або з Python
python -c "
import psycopg2
conn = psycopg2.connect('host=localhost dbname=learning_db user=admin password=admin123')
cursor = conn.cursor()
with open('sql_examples/05_advanced_analytics.sql') as f:
    cursor.execute(f.read())
conn.close()
"
```

---

## 🎯 Real-World Applications

### 1. E-Commerce Analytics Pipeline

**Scenario**: Компанія хоче real-time recommendations

**Solution**:
```python
# 1. ETL: Async extraction product/user data
pipeline = ETLPipeline()
await pipeline.run_parallel_pipelines(products, users)

# 2. Feature Store: Compute recommendation features
fs = FeatureStore()
product_features = fs.compute_product_features()
fs.save_features("product", product_features)

# 3. ML Model: Train на offline features
training_data = fs.get_training_dataset("product")
model.fit(training_data)

# 4. Serving: Fast lookup для recommendations
features = fs.get_features("product", [1,2,3])
recommendations = model.predict(features)
```

### 2. Churn Prediction System

**Scenario**: Передбачити які users churned

**SQL**: Extract features
```sql
-- Compute churn features
SELECT
    customer_id,
    days_since_last_order,
    total_orders,
    avg_order_value,
    -- ... more features
FROM customer_features
```

**Python**: Train model
```python
# Repository pattern для clean data access
repo = RepositoryFactory.create_customer_repository()
service = CustomerService(repo)

# Get features
customers = service.repository.get_all()
# Train model...
```

### 3. Real-time Data Warehouse

**Architecture**:
```
API Sources → Async ETL → PostgreSQL (staging)
                ↓
        Feature Store (transform)
                ↓
        Analytics DB (serving)
                ↓
        Dashboards / ML Models
```

---

## 💡 Best Practices Demonstrated

### Code Quality
- ✅ Type hints для type safety
- ✅ Dataclasses для domain models
- ✅ Context managers для resource management
- ✅ Error handling та logging
- ✅ Metrics collection

### Architecture
- ✅ SOLID principles
- ✅ Separation of concerns
- ✅ Dependency injection
- ✅ Interface segregation
- ✅ Factory pattern

### Data Engineering
- ✅ Batch processing з executemany
- ✅ UPSERT для idempotency
- ✅ Data validation
- ✅ Type-safe transformations
- ✅ Point-in-time correctness

### ML Engineering
- ✅ Feature store pattern
- ✅ Offline/Online feature split
- ✅ Feature versioning
- ✅ Model serving patterns
- ✅ A/B testing ready

---

## 🚀 Як Використовувати

### Для Навчання

**1. Почніть з базового модуля**:
- Async basics
- SQL fundamentals
- Python + PostgreSQL

**2. Перейдіть до advanced**:
```bash
# ETL Pipeline
python advanced_examples/etl/01_async_etl_pipeline.py

# Architectural Patterns
python advanced_examples/patterns/02_repository_pattern.py

# Feature Store
python advanced_examples/ml_pipeline/03_feature_store.py

# Advanced SQL
psql -U admin -d learning_db -f sql_examples/05_advanced_analytics.sql
```

**3. Експериментуйте**:
- Змінюйте data sources
- Додайте нові features
- Розширюйте patterns
- Інтегруйте з ML models

### Для Production

**Розширення до production**:
- [ ] Додати retry logic (tenacity library)
- [ ] Додати circuit breaker (pybreaker)
- [ ] Замінити print на proper logging
- [ ] Додати Prometheus metrics
- [ ] Додати distributed tracing
- [ ] Використати Redis для online features
- [ ] Додати data quality checks
- [ ] Створити Airflow DAGs
- [ ] Додати unit/integration tests
- [ ] Containerize з Docker
- [ ] Deploy на Kubernetes

---

## 📚 Рекомендовані Ресурси

### Books
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "The Data Warehouse Toolkit" - Ralph Kimball
- "Building Machine Learning Powered Applications" - Emmanuel Ameisen
- "Clean Architecture" - Robert C. Martin

### Tools для Production
- **Orchestration**: Airflow, Prefect, Dagster
- **Feature Store**: Feast, Tecton, SageMaker
- **Data Quality**: Great Expectations, Soda
- **Metrics**: Prometheus, Grafana
- **Tracing**: Jaeger, OpenTelemetry
- **Testing**: pytest, hypothesis

### Online Resources
- [Uber Engineering Blog](https://eng.uber.com/)
- [Netflix TechBlog](https://netflixtechblog.com/)
- [Airbnb Engineering](https://medium.com/airbnb-engineering)
- [Spotify Engineering](https://engineering.atspotify.com/)

---

## 🤝 Contribution

Хочете додати більше advanced patterns?

**Ideas for expansion**:
- [ ] Real-time streaming з Kafka
- [ ] Distributed processing з Dask/Ray
- [ ] ML model monitoring
- [ ] Data versioning з DVC
- [ ] GraphQL API для data access
- [ ] dbt models для transformations
- [ ] A/B testing framework
- [ ] Data catalog integration

---

## 📊 Comparison: Basic vs Advanced

| Aspect | Basic Module | Advanced Module |
|--------|-------------|-----------------|
| **Async** | Simple examples | Production ETL pipeline |
| **SQL** | SELECT, JOIN basics | Window functions, cohort analysis |
| **Architecture** | Direct DB calls | Repository pattern, DI |
| **ML** | - | Feature store, ML infrastructure |
| **Monitoring** | - | Metrics, observability |
| **Testing** | - | Mock repositories, TDD |
| **Complexity** | Learning-focused | Production-ready |

---

## ✅ Готово!

Тепер у вас є:
- ✅ **Базові знання** для початку роботи
- ✅ **Advanced patterns** для production
- ✅ **Real-world examples** з DS/DE практик
- ✅ **Modern best practices** та architecture
- ✅ **Practical use cases** для portfolio

**Next Steps**:
1. Пройдіть базовий модуль
2. Вивчіть advanced patterns
3. Застосуйте на власних проєктах
4. Додайте у portfolio

---

**Доповнено для Data Scientists & Data Engineers** 🚀

*Balance between theory and practice, sophistication and simplicity*
