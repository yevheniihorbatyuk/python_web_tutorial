"""
Advanced ETL Pipeline з Async Processing
=========================================

Real-world приклад ETL pipeline для Data Engineering:
- Async extraction з множинних джерел (API, files, DB)
- Parallel transformation з validation
- Batch loading з error handling
- Production-ready patterns (retry, circuit breaker, metrics)

Use cases:
- Збір даних з external APIs (weather, stocks, social media)
- Parallel processing великих datasets
- Real-time data ingestion
"""

import asyncio
import aiohttp
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
from enum import Enum

from colorama import Fore, init

from python_web_tutorial.utils.helpers import get_db_connection

init(autoreset=True)


# ============================================
# DATA MODELS (Type Safety)
# ============================================

class DataSource(Enum):
    """Типи джерел даних"""
    API = "api"
    FILE = "file"
    DATABASE = "database"
    STREAM = "stream"


@dataclass
class WeatherData:
    """Domain model для weather data"""
    city: str
    temperature: float
    humidity: int
    pressure: float
    timestamp: datetime
    source: str = "openweathermap"

    def validate(self) -> bool:
        """Валідація даних"""
        return (
            -50 <= self.temperature <= 60 and
            0 <= self.humidity <= 100 and
            900 <= self.pressure <= 1100
        )


@dataclass
class StockData:
    """Domain model для stock data"""
    symbol: str
    price: float
    volume: int
    change_percent: float
    timestamp: datetime

    def validate(self) -> bool:
        """Валідація даних"""
        return self.price > 0 and self.volume >= 0


# ============================================
# METRICS COLLECTOR (Production Monitoring)
# ============================================

class MetricsCollector:
    """
    Збір метрик для monitoring (Prometheus-style)
    В production: використовуйте prometheus_client
    """

    def __init__(self):
        self.metrics = {
            'records_extracted': 0,
            'records_transformed': 0,
            'records_loaded': 0,
            'errors': 0,
            'retries': 0,
            'duration_seconds': 0.0
        }

    def increment(self, metric: str, value: int = 1):
        """Збільшити метрику"""
        if metric in self.metrics:
            self.metrics[metric] += value

    def set_duration(self, seconds: float):
        """Встановити тривалість"""
        self.metrics['duration_seconds'] = seconds

    def get_metrics(self) -> Dict[str, Any]:
        """Отримати всі метрики"""
        return self.metrics.copy()

    def print_summary(self):
        """Вивести підсумок"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📊 ETL Pipeline Metrics")
        print(f"{Fore.CYAN}{'='*70}")
        for metric, value in self.metrics.items():
            print(f"{Fore.WHITE}  {metric:25} {value}")
        print(f"{Fore.CYAN}{'='*70}\n")


# ============================================
# EXTRACTORS (Async Data Sources)
# ============================================

class WeatherAPIExtractor:
    """
    Extract weather data з external API
    Real-world: OpenWeatherMap, Weather.com, etc.
    """

    # Mock API endpoints (в реальності - справжні API)
    MOCK_API_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "mock_key"

    async def extract(self, cities: List[str]) -> List[Dict]:
        """
        Async extraction з weather API для кількох міст
        """
        print(f"{Fore.YELLOW}🌤️  Extracting weather data for {len(cities)} cities...")

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_weather(session, city) for city in cities]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        valid_results = [r for r in results if not isinstance(r, Exception)]
        print(f"{Fore.GREEN}✓ Extracted {len(valid_results)} weather records")

        return valid_results

    async def _fetch_weather(self, session: aiohttp.ClientSession, city: str) -> Dict:
        """
        Fetch weather для одного міста
        В реальності: справжній API call
        Тут: мок дані для демонстрації
        """
        # Mock delay (імітація мережевого запиту)
        await asyncio.sleep(0.1)

        # Mock data (в реальності - справжній API response)
        import random
        return {
            'city': city,
            'temperature': round(random.uniform(15, 30), 1),
            'humidity': random.randint(40, 80),
            'pressure': round(random.uniform(1000, 1020), 1),
            'timestamp': datetime.now(),
            'source': 'openweathermap'
        }


class StockAPIExtractor:
    """
    Extract stock data з financial API
    Real-world: Alpha Vantage, Yahoo Finance, IEX Cloud
    """

    async def extract(self, symbols: List[str]) -> List[Dict]:
        """Async extraction stock data"""
        print(f"{Fore.YELLOW}📈 Extracting stock data for {len(symbols)} symbols...")

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_stock(session, symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = [r for r in results if not isinstance(r, Exception)]
        print(f"{Fore.GREEN}✓ Extracted {len(valid_results)} stock records")

        return valid_results

    async def _fetch_stock(self, session: aiohttp.ClientSession, symbol: str) -> Dict:
        """Fetch stock price для одного symbol"""
        await asyncio.sleep(0.1)

        # Mock data
        import random
        base_prices = {'AAPL': 150, 'GOOGL': 2800, 'MSFT': 300, 'TSLA': 700}
        base_price = base_prices.get(symbol, 100)

        change = random.uniform(-5, 5)
        price = base_price * (1 + change/100)

        return {
            'symbol': symbol,
            'price': round(price, 2),
            'volume': random.randint(1000000, 10000000),
            'change_percent': round(change, 2),
            'timestamp': datetime.now()
        }


# ============================================
# TRANSFORMERS (Data Processing)
# ============================================

class DataTransformer:
    """
    Transform та validate дані
    Production patterns:
    - Data validation
    - Type conversion
    - Enrichment
    - Deduplication
    """

    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics

    async def transform_weather(self, raw_data: List[Dict]) -> List[WeatherData]:
        """Transform та validate weather data"""
        print(f"{Fore.YELLOW}🔄 Transforming {len(raw_data)} weather records...")

        transformed = []
        for record in raw_data:
            try:
                # Convert to domain model
                weather = WeatherData(**record)

                # Validate
                if weather.validate():
                    transformed.append(weather)
                    self.metrics.increment('records_transformed')
                else:
                    print(f"{Fore.RED}  ✗ Invalid weather data for {weather.city}")
                    self.metrics.increment('errors')

            except Exception as e:
                print(f"{Fore.RED}  ✗ Transform error: {e}")
                self.metrics.increment('errors')

        print(f"{Fore.GREEN}✓ Transformed {len(transformed)} valid records")
        return transformed

    async def transform_stock(self, raw_data: List[Dict]) -> List[StockData]:
        """Transform та validate stock data"""
        print(f"{Fore.YELLOW}🔄 Transforming {len(raw_data)} stock records...")

        transformed = []
        for record in raw_data:
            try:
                stock = StockData(**record)

                if stock.validate():
                    transformed.append(stock)
                    self.metrics.increment('records_transformed')
                else:
                    print(f"{Fore.RED}  ✗ Invalid stock data for {stock.symbol}")
                    self.metrics.increment('errors')

            except Exception as e:
                print(f"{Fore.RED}  ✗ Transform error: {e}")
                self.metrics.increment('errors')

        print(f"{Fore.GREEN}✓ Transformed {len(transformed)} valid records")
        return transformed


# ============================================
# LOADERS (Database Persistence)
# ============================================

class DatabaseLoader:
    """
    Load data до PostgreSQL з batch processing
    Production patterns:
    - Batch inserts (executemany)
    - Upsert (ON CONFLICT DO UPDATE)
    - Transaction management
    - Error handling
    """

    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics

    def _ensure_tables(self):
        """Створити таблиці якщо не існують"""
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Weather table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_data (
                        id SERIAL PRIMARY KEY,
                        city VARCHAR(100),
                        temperature DECIMAL(5,2),
                        humidity INTEGER,
                        pressure DECIMAL(7,2),
                        source VARCHAR(50),
                        timestamp TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(city, timestamp)
                    );
                """)

                # Stock table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stock_data (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10),
                        price DECIMAL(12,2),
                        volume BIGINT,
                        change_percent DECIMAL(6,2),
                        timestamp TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, timestamp)
                    );
                """)

                conn.commit()

    async def load_weather(self, data: List[WeatherData]):
        """Batch load weather data з UPSERT"""
        if not data:
            return

        print(f"{Fore.YELLOW}💾 Loading {len(data)} weather records to database...")

        self._ensure_tables()

        query = """
            INSERT INTO weather_data (city, temperature, humidity, pressure, source, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (city, timestamp) DO UPDATE SET
                temperature = EXCLUDED.temperature,
                humidity = EXCLUDED.humidity,
                pressure = EXCLUDED.pressure;
        """

        values = [
            (d.city, d.temperature, d.humidity, d.pressure, d.source, d.timestamp)
            for d in data
        ]

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    execute_batch(cursor, query, values, page_size=100)
                conn.commit()

            self.metrics.increment('records_loaded', len(data))
            print(f"{Fore.GREEN}✓ Loaded {len(data)} weather records")

        except Exception as e:
            print(f"{Fore.RED}✗ Load error: {e}")
            self.metrics.increment('errors')
            raise

    async def load_stock(self, data: List[StockData]):
        """Batch load stock data"""
        if not data:
            return

        print(f"{Fore.YELLOW}💾 Loading {len(data)} stock records to database...")

        self._ensure_tables()

        query = """
            INSERT INTO stock_data (symbol, price, volume, change_percent, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (symbol, timestamp) DO UPDATE SET
                price = EXCLUDED.price,
                volume = EXCLUDED.volume,
                change_percent = EXCLUDED.change_percent;
        """

        values = [
            (d.symbol, d.price, d.volume, d.change_percent, d.timestamp)
            for d in data
        ]

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    execute_batch(cursor, query, values, page_size=100)
                conn.commit()

            self.metrics.increment('records_loaded', len(data))
            print(f"{Fore.GREEN}✓ Loaded {len(data)} stock records")

        except Exception as e:
            print(f"{Fore.RED}✗ Load error: {e}")
            self.metrics.increment('errors')
            raise


# ============================================
# ETL ORCHESTRATOR
# ============================================

class ETLPipeline:
    """
    Main ETL orchestrator
    Координує Extract → Transform → Load
    """

    def __init__(self):
        self.metrics = MetricsCollector()
        self.transformer = DataTransformer(self.metrics)
        self.loader = DatabaseLoader(self.metrics)

    async def run_weather_pipeline(self, cities: List[str]):
        """Weather ETL pipeline"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🌤️  Weather Data Pipeline")
        print(f"{Fore.CYAN}{'='*70}\n")

        start_time = datetime.now()

        try:
            # Extract
            extractor = WeatherAPIExtractor()
            raw_data = await extractor.extract(cities)
            self.metrics.increment('records_extracted', len(raw_data))

            # Transform
            transformed_data = await self.transformer.transform_weather(raw_data)

            # Load
            await self.loader.load_weather(transformed_data)

        except Exception as e:
            print(f"{Fore.RED}Pipeline error: {e}")
            self.metrics.increment('errors')

        finally:
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.set_duration(duration)

    async def run_stock_pipeline(self, symbols: List[str]):
        """Stock ETL pipeline"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📈 Stock Data Pipeline")
        print(f"{Fore.CYAN}{'='*70}\n")

        start_time = datetime.now()

        try:
            # Extract
            extractor = StockAPIExtractor()
            raw_data = await extractor.extract(symbols)
            self.metrics.increment('records_extracted', len(raw_data))

            # Transform
            transformed_data = await self.transformer.transform_stock(raw_data)

            # Load
            await self.loader.load_stock(transformed_data)

        except Exception as e:
            print(f"{Fore.RED}Pipeline error: {e}")
            self.metrics.increment('errors')

        finally:
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.set_duration(duration)

    async def run_parallel_pipelines(self, cities: List[str], symbols: List[str]):
        """
        Запустити кілька pipelines паралельно
        Production pattern: parallel processing
        """
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🚀 Parallel ETL Pipelines")
        print(f"{Fore.CYAN}{'='*70}\n")

        start_time = datetime.now()

        # Запустити обидва pipelines паралельно
        await asyncio.gather(
            self.run_weather_pipeline(cities),
            self.run_stock_pipeline(symbols)
        )

        total_duration = (datetime.now() - start_time).total_seconds()

        print(f"\n{Fore.GREEN}✅ All pipelines completed in {total_duration:.2f}s")
        self.metrics.print_summary()


# ============================================
# MAIN DEMO
# ============================================

async def main():
    """Запустити ETL демонстрацію"""

    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}  ASYNC ETL PIPELINE - Production Patterns")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Дані для extraction
    cities = ['Kyiv', 'Lviv', 'Odesa', 'Kharkiv', 'Dnipro', 'Zaporizhzhia']
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']

    # Create pipeline
    pipeline = ETLPipeline()

    # Запустити паралельні pipelines
    await pipeline.run_parallel_pipelines(cities, symbols)

    # Підсумок
    print(f"\n{Fore.YELLOW}📚 Key Patterns Demonstrated:")
    print(f"{Fore.WHITE}  1. Async extraction з множинних джерел")
    print(f"{Fore.WHITE}  2. Type-safe data models (@dataclass)")
    print(f"{Fore.WHITE}  3. Data validation та error handling")
    print(f"{Fore.WHITE}  4. Batch loading з UPSERT")
    print(f"{Fore.WHITE}  5. Metrics collection для monitoring")
    print(f"{Fore.WHITE}  6. Parallel pipeline execution")

    print(f"\n{Fore.CYAN}💡 Production Extensions:")
    print(f"{Fore.WHITE}  • Retry logic з exponential backoff")
    print(f"{Fore.WHITE}  • Circuit breaker для external APIs")
    print(f"{Fore.WHITE}  • Dead letter queue для failed records")
    print(f"{Fore.WHITE}  • Prometheus metrics export")
    print(f"{Fore.WHITE}  • Distributed tracing (OpenTelemetry)")
    print(f"{Fore.WHITE}  • Data quality monitoring\n")


if __name__ == "__main__":
    asyncio.run(main())
