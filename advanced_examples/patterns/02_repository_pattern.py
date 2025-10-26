"""
Repository Pattern + Dependency Injection
==========================================

Modern архітектурні паттерни для clean code:
- Repository Pattern: абстракція data access layer
- Dependency Injection: loose coupling
- Factory Pattern: object creation
- Unit of Work: transaction management

Переваги для DS/DE:
- Легко тестувати (mock repositories)
- Легко змінювати БД (PostgreSQL → BigQuery)
- Clean separation of concerns
- Type-safe з Python type hints
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor
from colorama import Fore, init

from python_web_tutorial.utils.db import ConnectionPool, DatabaseConfig, get_cursor

init(autoreset=True)

# ============================================
# DOMAIN MODELS
# ============================================

@dataclass
class Customer:
    """Domain model - незалежний від БД"""
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    city: str = ""
    registration_date: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class Order:
    """Order domain model"""
    id: Optional[int] = None
    customer_id: int = 0
    total_amount: float = 0.0
    status: str = "pending"
    order_date: Optional[datetime] = None


# ============================================
# REPOSITORY INTERFACES (Abstract)
# ============================================

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    """
    Generic repository interface
    Визначає контракт для всіх repositories
    """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Знайти по ID"""
        pass

    @abstractmethod
    def get_all(self, limit: int = 100) -> List[T]:
        """Отримати всі записи"""
        pass

    @abstractmethod
    def add(self, entity: T) -> T:
        """Додати новий запис"""
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Оновити запис"""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Видалити запис"""
        pass


class ICustomerRepository(IRepository[Customer]):
    """
    Customer-specific repository interface
    Додає domain-specific методи
    """

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Customer]:
        """Знайти по email"""
        pass

    @abstractmethod
    def find_by_city(self, city: str) -> List[Customer]:
        """Знайти всіх клієнтів з міста"""
        pass

    @abstractmethod
    def get_top_customers(self, limit: int = 10) -> List[Customer]:
        """Топ клієнтів за сумою покупок"""
        pass


# ============================================
# CONCRETE IMPLEMENTATIONS
# ============================================

class PostgresCustomerRepository(ICustomerRepository):
    """
    PostgreSQL implementation of customer repository
    Приховує всі деталі роботи з БД
    """

    def __init__(
        self,
        config: Optional[DatabaseConfig] = None,
        *,
        connection_pool: Optional[ConnectionPool] = None,
    ) -> None:
        if config and connection_pool:
            raise ValueError("Provide either config or connection_pool, not both")
        self._config: Optional[DatabaseConfig] = config
        self._connection_pool = connection_pool

    def _get_config(self) -> DatabaseConfig:
        if self._config is None:
            self._config = DatabaseConfig()
        return self._config

    @contextmanager
    def _cursor_from_pool(self):
        if self._connection_pool is None:
            raise RuntimeError("Connection pool is not configured")
        with self._connection_pool.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                yield cursor

    def _cursor_manager(self):
        return (
            self._cursor_from_pool()
            if self._connection_pool
            else get_cursor(self._get_config(), dict_cursor=True)
        )

    def get_by_id(self, id: int) -> Optional[Customer]:
        """Get customer by ID"""
        with self._cursor_manager() as cursor:
            cursor.execute("SELECT * FROM customers WHERE id = %s", (id,))
            row = cursor.fetchone()
            return self._map_to_entity(row) if row else None

    def get_all(self, limit: int = 100) -> List[Customer]:
        """Get all customers"""
        with self._cursor_manager() as cursor:
            cursor.execute("SELECT * FROM customers LIMIT %s", (limit,))
            rows = cursor.fetchall()
            return [self._map_to_entity(row) for row in rows]

    def add(self, entity: Customer) -> Customer:
        """Add new customer"""
        query = """
            INSERT INTO customers (first_name, last_name, email, city, registration_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, first_name, last_name, email, city, registration_date;
        """

        with self._cursor_manager() as cursor:
            cursor.execute(
                query,
                (
                    entity.first_name,
                    entity.last_name,
                    entity.email,
                    entity.city,
                    entity.registration_date or datetime.now(),
                ),
            )
            row = cursor.fetchone()
            return self._map_to_entity(row)

    def update(self, entity: Customer) -> Customer:
        """Update customer"""
        query = """
            UPDATE customers
            SET first_name = %s, last_name = %s, email = %s, city = %s
            WHERE id = %s
            RETURNING id, first_name, last_name, email, city, registration_date;
        """

        with self._cursor_manager() as cursor:
            cursor.execute(
                query,
                (
                    entity.first_name,
                    entity.last_name,
                    entity.email,
                    entity.city,
                    entity.id,
                ),
            )
            row = cursor.fetchone()
            return self._map_to_entity(row) if row else entity

    def delete(self, id: int) -> bool:
        """Delete customer"""
        with self._cursor_manager() as cursor:
            cursor.execute("DELETE FROM customers WHERE id = %s", (id,))
            return cursor.rowcount > 0

    def find_by_email(self, email: str) -> Optional[Customer]:
        """Find by email"""
        with self._cursor_manager() as cursor:
            cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
            row = cursor.fetchone()
            return self._map_to_entity(row) if row else None

    def find_by_city(self, city: str) -> List[Customer]:
        """Find all customers from city"""
        with self._cursor_manager() as cursor:
            cursor.execute("SELECT * FROM customers WHERE city = %s", (city,))
            rows = cursor.fetchall()
            return [self._map_to_entity(row) for row in rows]

    def get_top_customers(self, limit: int = 10) -> List[Customer]:
        """Get top customers by total spending"""
        query = """
            SELECT c.*, COALESCE(SUM(o.total_amount), 0) as total_spent
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id
            ORDER BY total_spent DESC
            LIMIT %s;
        """

        with self._cursor_manager() as cursor:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [self._map_to_entity(row) for row in rows]

    @staticmethod
    def _map_to_entity(row: dict) -> Customer:
        """Map database row to domain entity"""
        return Customer(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            city=row['city'],
            registration_date=row.get('registration_date')
        )


# ============================================
# IN-MEMORY IMPLEMENTATION (for testing)
# ============================================

class InMemoryCustomerRepository(ICustomerRepository):
    """
    In-memory implementation для тестування
    Не потребує БД - ідеально для unit tests
    """

    def __init__(self):
        self._storage: dict[int, Customer] = {}
        self._next_id = 1

    def get_by_id(self, id: int) -> Optional[Customer]:
        return self._storage.get(id)

    def get_all(self, limit: int = 100) -> List[Customer]:
        return list(self._storage.values())[:limit]

    def add(self, entity: Customer) -> Customer:
        entity.id = self._next_id
        self._next_id += 1
        self._storage[entity.id] = entity
        return entity

    def update(self, entity: Customer) -> Customer:
        if entity.id and entity.id in self._storage:
            self._storage[entity.id] = entity
        return entity

    def delete(self, id: int) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False

    def find_by_email(self, email: str) -> Optional[Customer]:
        for customer in self._storage.values():
            if customer.email == email:
                return customer
        return None

    def find_by_city(self, city: str) -> List[Customer]:
        return [c for c in self._storage.values() if c.city == city]

    def get_top_customers(self, limit: int = 10) -> List[Customer]:
        # Mock implementation
        return list(self._storage.values())[:limit]


# ============================================
# SERVICE LAYER (Business Logic)
# ============================================

class CustomerService:
    """
    Service layer - містить business logic
    Використовує repository через dependency injection
    """

    def __init__(self, repository: ICustomerRepository):
        self.repository = repository

    def register_customer(self, first_name: str, last_name: str,
                         email: str, city: str) -> Optional[Customer]:
        """
        Business logic: register new customer
        Validation + persistence
        """
        # Validation
        if not email or '@' not in email:
            raise ValueError("Invalid email")

        # Check if exists
        existing = self.repository.find_by_email(email)
        if existing:
            print(f"{Fore.YELLOW}⚠️  Customer with email {email} already exists")
            return existing

        # Create new customer
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            city=city,
            registration_date=datetime.now()
        )

        return self.repository.add(customer)

    def get_customers_by_city(self, city: str) -> List[Customer]:
        """Get all customers from specific city"""
        return self.repository.find_by_city(city)

    def get_customer_summary(self, customer_id: int) -> Optional[dict]:
        """
        Complex business logic: get customer with summary
        В production: може включати ML predictions, recommendations, etc.
        """
        customer = self.repository.get_by_id(customer_id)
        if not customer:
            return None

        return {
            'customer': customer,
            'full_name': customer.full_name,
            'city': customer.city,
            # В production: додати order history, predictions, segments
        }


# ============================================
# FACTORY PATTERN
# ============================================

class RepositoryFactory:
    """
    Factory для створення repositories
    Дозволяє легко переключатись між implementations
    """

    @staticmethod
    def create_customer_repository(
        type: str = "postgres",
        *,
        config: Optional[DatabaseConfig] = None,
        connection_pool: Optional[ConnectionPool] = None,
    ) -> ICustomerRepository:
        """
        Create customer repository based on type
        """
        if type == "postgres":
            if config and connection_pool:
                raise ValueError("Provide either config or connection_pool, not both")
            if connection_pool:
                return PostgresCustomerRepository(connection_pool=connection_pool)
            return PostgresCustomerRepository(config=config)
        elif type == "memory":
            return InMemoryCustomerRepository()
        else:
            raise ValueError(f"Unknown repository type: {type}")


# ============================================
# DEPENDENCY INJECTION CONTAINER
# ============================================

class DIContainer:
    """
    Simple Dependency Injection container
    В production: використовуйте dependency_injector або similar
    """

    def __init__(self):
        self._services = {}

    def register(self, interface: type, implementation: any):
        """Register service"""
        self._services[interface] = implementation

    def resolve(self, interface: type) -> any:
        """Resolve service"""
        return self._services.get(interface)


# ============================================
# DEMO
# ============================================

def demo_repository_pattern():
    """Демонстрація Repository Pattern"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}1. Repository Pattern Demo")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Create repository (можна легко змінити на InMemory)
    repo = RepositoryFactory.create_customer_repository("postgres")

    # Get all customers
    print(f"{Fore.YELLOW}📋 All customers:")
    customers = repo.get_all(limit=5)
    for customer in customers:
        print(f"{Fore.WHITE}  • {customer.full_name} ({customer.email}) - {customer.city}")

    # Find by city
    print(f"\n{Fore.YELLOW}🌍 Customers from Kyiv:")
    kyiv_customers = repo.find_by_city("Kyiv")
    for customer in kyiv_customers:
        print(f"{Fore.WHITE}  • {customer.full_name}")


def demo_service_layer():
    """Демонстрація Service Layer з DI"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}2. Service Layer + Dependency Injection")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Setup DI Container
    container = DIContainer()
    container.register(
        ICustomerRepository,
        RepositoryFactory.create_customer_repository("postgres")
    )

    # Create service з dependency injection
    repo = container.resolve(ICustomerRepository)
    service = CustomerService(repo)

    # Business logic через service
    print(f"{Fore.YELLOW}👤 Register new customer:")
    try:
        new_customer = service.register_customer(
            first_name="Senior",
            last_name="DataEngineer",
            email="senior@datateam.com",
            city="Kyiv"
        )
        print(f"{Fore.GREEN}✓ Registered: {new_customer.full_name}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}")

    # Get summary
    print(f"\n{Fore.YELLOW}📊 Customer summary:")
    summary = service.get_customer_summary(1)
    if summary:
        print(f"{Fore.WHITE}  Name: {summary['full_name']}")
        print(f"{Fore.WHITE}  City: {summary['city']}")


def demo_testing_with_mock():
    """Демонстрація testing з InMemory repository"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}3. Unit Testing з Mock Repository")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Create in-memory repository для тестів
    repo = InMemoryCustomerRepository()
    service = CustomerService(repo)

    # Test: add customers
    print(f"{Fore.YELLOW}🧪 Adding test customers...")
    customer1 = service.register_customer("Test", "User1", "test1@test.com", "Kyiv")
    customer2 = service.register_customer("Test", "User2", "test2@test.com", "Lviv")

    # Test: find by city
    kyiv_customers = service.get_customers_by_city("Kyiv")
    print(f"{Fore.GREEN}✓ Found {len(kyiv_customers)} customers in Kyiv")

    # Test: duplicate email
    print(f"\n{Fore.YELLOW}🧪 Testing duplicate email...")
    duplicate = service.register_customer("Test", "User3", "test1@test.com", "Odesa")
    print(f"{Fore.GREEN}✓ Duplicate handled correctly")


def main():
    """Main demo"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}  ARCHITECTURAL PATTERNS - Production Best Practices")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Run demos
    demo_repository_pattern()
    demo_service_layer()
    demo_testing_with_mock()

    # Summary
    print(f"\n{Fore.YELLOW}📚 Key Patterns:")
    print(f"{Fore.WHITE}  1. Repository Pattern - абстракція data access")
    print(f"{Fore.WHITE}  2. Dependency Injection - loose coupling")
    print(f"{Fore.WHITE}  3. Factory Pattern - flexible object creation")
    print(f"{Fore.WHITE}  4. Service Layer - business logic separation")
    print(f"{Fore.WHITE}  5. Interface Segregation - clean contracts")

    print(f"\n{Fore.CYAN}💡 Benefits:")
    print(f"{Fore.WHITE}  ✓ Легко тестувати (mock repositories)")
    print(f"{Fore.WHITE}  ✓ Легко змінювати БД")
    print(f"{Fore.WHITE}  ✓ Clean code structure")
    print(f"{Fore.WHITE}  ✓ Type-safe з type hints")
    print(f"{Fore.WHITE}  ✓ SOLID principles\n")


if __name__ == "__main__":
    main()
