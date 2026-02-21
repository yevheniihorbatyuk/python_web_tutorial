"""
Module 8.1: SQLAlchemy ORM - Advanced Patterns
==============================================

МЕТА МОДУЛЯ:
  Навчитись працювати з SQL базами даних через ORM, який автоматично
  перетворює Python классі на таблиці БД.

ЗМІСТ:
  1. Моделі даних: User → Address → City → Country (ієрархія)
  2. CRUD операції: Create, Read, Update, Delete
  3. Оптимізація запитів: Eager loading (1 запит) vs Lazy loading (N+1)
  4. Агрегації: Підрахунок, середні значення, групування
  5. Транзакції: Atоmicity (все або нічого)

ПРАКТИЧНІ ПРИКЛАДИ:
  - Знайти всіх користувачів з України
  - Підрахувати скільки користувачів у кожній країні
  - Отримати топ-10 користувачів по рейтингу профіля

ЧОМУ ЦЕ ВАЖЛИВО:
  ✓ N+1 проблема: 1000 користувачів × 1 запит на адресу = 1000 запитів!
    Eager loading: 1 запит замість 1000!
  ✓ ACID транзакції: Якщо помилка між INSERT'ами, скасовуємо все
  ✓ Міграції: Змінювати схему БД без втрати даних

Author: Senior Data Science Engineer
"""

# ─── Нотатка про стиль коду ──────────────────────────────────────────────────
# Цей файл: SQLAlchemy 1.x/2.0-compatible стиль
#   Column(), Integer, declarative_base(), sessionmaker(bind=engine)
#   Широко зустрічається у legacy проектах (2018-2023).
#
# Сучасний SQLAlchemy 2.0 стиль (рекомендовано для нових проектів):
#   mapped_column(), Mapped[], DeclarativeBase, async_sessionmaker()
#   Приклад: ./sqlalchemy_examples/models.py
#
# Обидва вивчаються навмисно — на реальних проектах ти зустрінеш обидва.
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime,
    ForeignKey, Boolean, Float, func, and_, or_, desc,
    Text, Date, Numeric, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
import logging

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use SQLite for demo (can be replaced with PostgreSQL)
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL logging
)

Base = declarative_base()
Session = sessionmaker(bind=engine)


# ============================================================================
# DATA MODELS - HIERARCHICAL STRUCTURE
# ============================================================================

class Country(Base):
    """
    МОДЕЛЬ КРАЇНИ

    Представляє країну у База Даних з базовою інформацією.

    ЗБЕРІГАЄ:
      - id: Унікальний ідентифікатор (Primary Key)
      - name: Назва країни (UNIQUE = не може бути 2 однакові)
      - code: ISO код (UA = Україна, PL = Польща, DE = Німеччина)
      - population: Населення (для аналізу)
      - gdp_per_capita: ВВП на душу населення (економічна метрика)
      - cities: Зворотний зв'язок на міста (one-to-many)

    RELATIONSHIP ЛОГІКА:
      - 1 Country → Many Cities (один до багатьох)
      - cascade="all, delete-orphan": Якщо видалити країну,
        то всі дочірні міста теж видаляються автоматично
      - back_populates="country": Синхронізація з City.country

    INDEX:
      - idx_country_code: Індекс на code для швидких пошуків
      - Пошук "знайди країну з кодом UA" буде швидким (log n)
    """
    __tablename__ = "countries"  # Ім'я таблиці у БД

    # PRIMARY KEY: Унікальний ідентифікатор кожного рядка
    id = Column(Integer, primary_key=True, index=True)

    # UNIQUE: Гарантує що не буде 2 однакові назви країн
    name = Column(String(100), unique=True, nullable=False, index=True)

    # ISO 3166-1 alpha-3 код (UA, PL, DE)
    code = Column(String(3), unique=True, nullable=False)  # ISO 3166-1 alpha-3

    # NULLABLE: Ці поля можуть бути порожні (NULL у БД)
    population = Column(Integer, nullable=True)
    gdp_per_capita = Column(Float, nullable=True)  # For analysis

    # TIMESTAMP: Коли записано у БД (автоматично заповнюється)
    created_at = Column(DateTime, default=datetime.utcnow)

    # RELATIONSHIP: Посилання на всі міста цієї країни
    # back_populates="country" = двосторонній зв'язок з City
    # cascade="all, delete-orphan" = видалити дочірні при видаленні батька
    cities = relationship("City", back_populates="country", cascade="all, delete-orphan")

    # INDEXES: Оптимізація для швидких запитів
    __table_args__ = (
        Index('idx_country_code', 'code'),  # Пошук по коду швидший
    )

    def __repr__(self):
        """Як виглядає об'єкт при print()"""
        return f"<Country {self.name} ({self.code})>"


class City(Base):
    """Represents a city with geographic and demographic data."""
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    latitude = Column(Float, nullable=True)  # For geo queries
    longitude = Column(Float, nullable=True)
    population = Column(Integer, nullable=True)
    is_capital = Column(Boolean, default=False)
    timezone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    country = relationship("Country", back_populates="cities")
    addresses = relationship("Address", back_populates="city", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_city_country_name', 'country_id', 'name'),
    )

    def __repr__(self):
        return f"<City {self.name}>"


class Address(Base):
    """Represents a residential or business address."""
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    street_name = Column(String(200), nullable=False)
    street_number = Column(String(20), nullable=True)
    postal_code = Column(String(20), nullable=True)
    is_residential = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    city = relationship("City", back_populates="addresses")
    users = relationship("User", back_populates="address")

    __table_args__ = (
        Index('idx_address_city_postal', 'city_id', 'postal_code'),
    )

    def __repr__(self):
        return f"<Address {self.street_name}, {self.city_id}>"


class User(Base):
    """Represents a user with profile and contact information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)

    # Address relationship
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=True, index=True)

    # Account metadata
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Data Science fields
    profile_score = Column(Float, default=0.0)  # User reputation/activity score
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    address = relationship("Address", back_populates="users")

    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_registration_date', 'registration_date'),
    )

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def update_last_login(self) -> None:
        """Update user's last login timestamp."""
        self.last_login = datetime.utcnow()


# ============================================================================
# DATABASE OPERATIONS - ADVANCED CRUD
# ============================================================================

def seed_database(session: Session) -> None:
    """
    Seed database with sample data.
    Demonstrates batch operations and relationships.
    """
    logger.info("Seeding database...")

    # Create countries
    countries_data = [
        {"name": "Ukraine", "code": "UKR", "population": 41000000, "gdp_per_capita": 4500},
        {"name": "Poland", "code": "POL", "population": 38000000, "gdp_per_capita": 17000},
        {"name": "Germany", "code": "DEU", "population": 83000000, "gdp_per_capita": 48000},
    ]

    countries = []
    for country_data in countries_data:
        country = Country(**country_data)
        countries.append(country)

    session.add_all(countries)
    session.flush()  # Get IDs without committing

    # Create cities
    cities_data = [
        {"name": "Kyiv", "country_id": countries[0].id, "population": 3000000, "is_capital": True, "timezone": "EET"},
        {"name": "Kharkiv", "country_id": countries[0].id, "population": 1400000, "is_capital": False},
        {"name": "Odesa", "country_id": countries[0].id, "population": 1000000, "is_capital": False},
        {"name": "Warsaw", "country_id": countries[1].id, "population": 860000, "is_capital": True, "timezone": "CET"},
        {"name": "Berlin", "country_id": countries[2].id, "population": 3600000, "is_capital": True, "timezone": "CET"},
    ]

    cities = []
    for city_data in cities_data:
        city = City(**city_data)
        cities.append(city)

    session.add_all(cities)
    session.flush()

    # Create addresses
    addresses_data = [
        {"city_id": cities[0].id, "street_name": "Khreschatyk Street", "postal_code": "01001"},
        {"city_id": cities[0].id, "street_name": "Pushkin Street", "postal_code": "01004"},
        {"city_id": cities[1].id, "street_name": "Sumska Street", "postal_code": "61000"},
        {"city_id": cities[3].id, "street_name": "Marszalkowska Street", "postal_code": "00-075"},
        {"city_id": cities[4].id, "street_name": "Unter den Linden", "postal_code": "10117"},
    ]

    addresses = []
    for address_data in addresses_data:
        address = Address(**address_data)
        addresses.append(address)

    session.add_all(addresses)
    session.flush()

    # Create users
    users_data = [
        {
            "username": "ivanov_ds",
            "email": "ivan.data@example.com",
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "address_id": addresses[0].id,
            "profile_score": 85.5,
        },
        {
            "username": "mariya_ml",
            "email": "mariya.ml@example.com",
            "first_name": "Mariya",
            "last_name": "Petrova",
            "address_id": addresses[1].id,
            "profile_score": 92.0,
        },
        {
            "username": "sergey_db",
            "email": "sergey@example.com",
            "first_name": "Sergey",
            "last_name": "Sidorov",
            "address_id": addresses[2].id,
            "profile_score": 78.5,
        },
        {
            "username": "anna_web",
            "email": "anna.web@example.com",
            "first_name": "Anna",
            "last_name": "Kowalski",
            "address_id": addresses[3].id,
            "profile_score": 88.0,
        },
    ]

    users = []
    for user_data in users_data:
        user = User(**user_data)
        users.append(user)

    session.add_all(users)
    session.commit()
    logger.info("✓ Database seeded with sample data")


# ============================================================================
# ADVANCED QUERYING PATTERNS
# ============================================================================

class UserRepository:
    """Repository pattern for User operations - handles all database queries."""

    def __init__(self, session: Session):
        self.session = session

    def find_users_by_country(self, country_name: str) -> List[User]:
        """
        Find all users living in a specific country.
        Demonstrates: JOIN across 3 tables, relationship navigation.
        """
        return self.session.query(User).join(
            Address, User.address_id == Address.id
        ).join(
            City, Address.city_id == City.id
        ).join(
            Country, City.country_id == Country.id
        ).filter(
            Country.name == country_name,
            User.is_active == True
        ).all()

    def find_users_in_city(self, city_name: str) -> List[User]:
        """Find all users in a specific city."""
        return self.session.query(User).join(
            Address
        ).join(
            City
        ).filter(
            City.name == city_name
        ).all()

    def get_users_with_addresses(self) -> List[User]:
        """
        Get users with their address information.
        Demonstrates: eager loading to prevent N+1 queries.
        """
        from sqlalchemy.orm import joinedload

        return self.session.query(User).options(
            joinedload(User.address).joinedload(Address.city).joinedload(City.country)
        ).all()

    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get statistical data about users.
        Demonstrates: aggregation functions for Data Science analysis.
        """
        stats = {
            "total_users": self.session.query(func.count(User.id)).scalar(),
            "active_users": self.session.query(func.count(User.id)).filter(
                User.is_active == True
            ).scalar(),
            "verified_users": self.session.query(func.count(User.id)).filter(
                User.is_verified == True
            ).scalar(),
            "average_profile_score": self.session.query(
                func.avg(User.profile_score)
            ).scalar(),
            "max_profile_score": self.session.query(
                func.max(User.profile_score)
            ).scalar(),
            "min_profile_score": self.session.query(
                func.min(User.profile_score)
            ).scalar(),
        }
        return stats

    def get_users_ranked_by_activity(self, limit: int = 10) -> List[User]:
        """Get top users by profile score."""
        return self.session.query(User).filter(
            User.is_active == True
        ).order_by(
            desc(User.profile_score)
        ).limit(limit).all()

    def find_active_users_by_registration_date(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[User]:
        """Find users registered within a date range."""
        return self.session.query(User).filter(
            and_(
                User.registration_date >= start_date,
                User.registration_date <= end_date,
                User.is_active == True
            )
        ).all()

    def search_users(self, query: str) -> List[User]:
        """Search users by username or email."""
        search_term = f"%{query}%"
        return self.session.query(User).filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        ).all()


class CountryRepository:
    """Repository for Country operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_all_countries_with_cities(self) -> List[Country]:
        """Get all countries with their cities."""
        from sqlalchemy.orm import joinedload

        return self.session.query(Country).options(
            joinedload(Country.cities)
        ).all()

    def get_country_statistics(self) -> Dict[str, Any]:
        """Get statistics about countries and their users."""
        countries = self.session.query(Country).all()

        stats = {}
        for country in countries:
            user_count = self.session.query(func.count(User.id)).join(
                Address
            ).join(
                City
            ).filter(
                City.country_id == country.id
            ).scalar()

            stats[country.name] = {
                "gdp_per_capita": country.gdp_per_capita,
                "population": country.population,
                "users_in_system": user_count or 0,
            }

        return stats


# ============================================================================
# DATA SCIENCE ANALYTICS
# ============================================================================

class DataScienceAnalytics:
    """Analytics and insights for Data Science applications."""

    def __init__(self, session: Session):
        self.session = session

    def get_user_distribution_by_country(self) -> Dict[str, int]:
        """
        Analyze user distribution across countries.
        Use case: Market analysis, user acquisition strategy.
        """
        result = self.session.query(
            Country.name,
            func.count(User.id).label('user_count')
        ).join(
            City
        ).join(
            Address
        ).join(
            User
        ).group_by(
            Country.name
        ).all()

        return {country: count for country, count in result}

    def get_user_metrics_by_registration_cohort(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze users by registration month (cohort analysis).
        Use case: Retention analysis, growth metrics.
        """
        from sqlalchemy import func

        result = self.session.query(
            func.strftime('%Y-%m', User.registration_date).label('cohort'),
            func.count(User.id).label('count'),
            func.avg(User.profile_score).label('avg_score'),
        ).group_by('cohort').order_by('cohort').all()

        return {
            cohort: {
                'users': count,
                'avg_profile_score': float(avg_score or 0)
            }
            for cohort, count, avg_score in result
        }

    def identify_high_value_users(self, percentile: int = 75) -> List[User]:
        """
        Identify high-value users (top performers).
        Use case: VIP identification, targeted campaigns.
        """
        percentile_value = self.session.query(
            func.percentile_cont(percentile/100.0)
            .within_group(User.profile_score)
        ).scalar()

        return self.session.query(User).filter(
            User.profile_score >= percentile_value,
            User.is_active == True
        ).order_by(desc(User.profile_score)).all()


# ============================================================================
# TRANSACTIONS & ERROR HANDLING
# ============================================================================

def create_user_with_address(
    session: Session,
    user_data: Dict[str, Any],
    address_data: Dict[str, Any],
    city_id: int
) -> Optional[User]:
    """
    Create a user with associated address.
    Demonstrates: Transactions, rollback on error, cascade operations.
    """
    try:
        # Create address
        address = Address(city_id=city_id, **address_data)
        session.add(address)
        session.flush()  # Get address.id

        # Create user with address
        user_data['address_id'] = address.id
        user = User(**user_data)
        session.add(user)
        session.commit()

        logger.info(f"✓ Created user {user.username} with address")
        return user

    except Exception as e:
        session.rollback()
        logger.error(f"✗ Error creating user: {str(e)}")
        return None


# ============================================================================
# MAIN EXECUTION - DEMONSTRATIONS
# ============================================================================

def main():
    """Run demonstrations of SQLAlchemy ORM patterns."""

    # Create tables
    Base.metadata.create_all(engine)
    logger.info("✓ Database tables created")

    # Get session
    session = Session()

    # Seed database
    seed_database(session)

    # ---- DEMONSTRATIONS ----
    logger.info("\n" + "="*80)
    logger.info("SQLAlchemy ORM - Advanced Patterns Demonstration")
    logger.info("="*80)

    # 1. Find users in Ukraine
    logger.info("\n[1] Users living in Ukraine:")
    user_repo = UserRepository(session)
    ukraine_users = user_repo.find_users_by_country("Ukraine")
    for user in ukraine_users:
        logger.info(f"  - {user.full_name} ({user.email})")
        if user.address:
            logger.info(f"    Address: {user.address.street_name}, {user.address.city.name}")

    # 2. Users by city
    logger.info("\n[2] Users in Kyiv:")
    kyiv_users = user_repo.find_users_in_city("Kyiv")
    for user in kyiv_users:
        logger.info(f"  - {user.full_name}")

    # 3. User statistics
    logger.info("\n[3] User Statistics:")
    stats = user_repo.get_user_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            logger.info(f"  - {key}: {value:.2f}")
        else:
            logger.info(f"  - {key}: {value}")

    # 4. Top users by activity
    logger.info("\n[4] Top Users by Profile Score:")
    top_users = user_repo.get_users_ranked_by_activity(limit=5)
    for i, user in enumerate(top_users, 1):
        logger.info(f"  {i}. {user.full_name} - Score: {user.profile_score}")

    # 5. Country statistics
    logger.info("\n[5] Country Statistics:")
    country_repo = CountryRepository(session)
    country_stats = country_repo.get_country_statistics()
    for country, stats in country_stats.items():
        logger.info(f"  - {country}: {stats['users_in_system']} users")

    # 6. Data Science Analytics
    logger.info("\n[6] User Distribution by Country:")
    ds_analytics = DataScienceAnalytics(session)
    distribution = ds_analytics.get_user_distribution_by_country()
    for country, count in distribution.items():
        logger.info(f"  - {country}: {count} users")

    # 7. Create new user with address
    logger.info("\n[7] Creating new user with address:")
    new_user = create_user_with_address(
        session,
        user_data={
            "username": "nova_user",
            "email": "nova@example.com",
            "first_name": "Nova",
            "last_name": "User",
            "profile_score": 75.0,
        },
        address_data={
            "street_name": "New Street",
            "postal_code": "01001",
        },
        city_id=1  # Kyiv
    )
    if new_user:
        logger.info(f"  ✓ User created: {new_user.username}")

    # 8. Search functionality
    logger.info("\n[8] Search results for 'data':")
    search_results = user_repo.search_users("data")
    for user in search_results:
        logger.info(f"  - {user.full_name} ({user.username})")

    logger.info("\n" + "="*80)
    logger.info("✓ All demonstrations completed successfully!")
    logger.info("="*80 + "\n")

    session.close()


if __name__ == "__main__":
    main()
