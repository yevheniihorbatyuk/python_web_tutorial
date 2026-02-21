# Design Patterns для Junior Python Developer

Три паттерни які ви зустрінете в реальних проектах протягом першого місяця роботи.

---

## Singleton

**Проблема:** Ресурс (підключення до БД, конфіг, логер) має існувати в одному екземплярі.

**Python реалізація:**

```python
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connected = False
        return cls._instance

    def connect(self, url: str) -> None:
        if not self._connected:
            print(f"Connecting to {url}...")
            self._connected = True

    def query(self, sql: str) -> list:
        if not self._connected:
            raise RuntimeError("Not connected")
        return []  # реальна логіка

# Перевірка
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # True — один об'єкт
```

**Де зустрічається:**
- SQLAlchemy engine (`create_engine()` зазвичай один на додаток)
- `logging.getLogger(name)` — повертає той самий логер для однакового імені
- FastAPI `app = FastAPI()` — один на процес

**Коли НЕ використовувати:**
- Коли потрібні тести (глобальний стан → складна ізоляція)
- Краще: передавати залежність через конструктор (DI), а Singleton — у DI-контейнері

---

## Factory

**Проблема:** Код знає що хоче створити, але не знає заздалегідь *яку* конкретну реалізацію.

```python
from abc import ABC, abstractmethod

class Message(ABC):
    @abstractmethod
    def send(self, recipient: str, text: str) -> str: ...

class EmailMessage(Message):
    def send(self, recipient, text):
        return f"Email to {recipient}: {text}"

class SMSMessage(Message):
    def send(self, recipient, text):
        return f"SMS to +{recipient}: {text[:160]}"  # SMS обмежений 160 символами

class PushMessage(Message):
    def send(self, recipient, text):
        return f"Push [{recipient}]: {text}"

# Factory Function (простіше — для більшості випадків достатньо)
def create_message(channel: str) -> Message:
    channels = {
        "email": EmailMessage,
        "sms": SMSMessage,
        "push": PushMessage,
    }
    cls = channels.get(channel)
    if cls is None:
        raise ValueError(f"Unknown channel: {channel}. Choose from: {list(channels)}")
    return cls()

# Factory Method (OCP: додати новий канал без зміни factory)
class MessageFactory:
    _registry: dict[str, type[Message]] = {}

    @classmethod
    def register(cls, channel: str):
        """Decorator to register a new message type."""
        def decorator(message_cls: type[Message]):
            cls._registry[channel] = message_cls
            return message_cls
        return decorator

    @classmethod
    def create(cls, channel: str) -> Message:
        msg_cls = cls._registry.get(channel)
        if msg_cls is None:
            raise ValueError(f"Unknown channel: {channel}")
        return msg_cls()

@MessageFactory.register("slack")
class SlackMessage(Message):
    def send(self, recipient, text):
        return f"Slack @{recipient}: {text}"
```

**Де зустрічається:**
- SQLAlchemy `create_engine("postgresql://...")` — вибирає правильний діалект
- FastAPI `Depends()` — DI-factory для залежностей
- `logging.getLogger()` — factory для логерів

---

## Adapter

**Проблема:** Стороннє API має інтерфейс відмінний від того що очікує ваш код.

```python
# Старе (legacy) API яке не можна змінити
class LegacyPaymentAPI:
    def make_payment(self, amount_cents: int, card_number: str) -> dict:
        # Стара система: суми в центах, картка без форматування
        return {"status": "ok", "transaction_id": "TXN123"}

# Новий інтерфейс вашого додатку
class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount_usd: float, card: str) -> str:
        """Returns transaction ID."""
        ...

# Adapter — обгортає legacy в новий інтерфейс
class LegacyPaymentAdapter(PaymentProcessor):
    def __init__(self, legacy_api: LegacyPaymentAPI):
        self._api = legacy_api

    def charge(self, amount_usd: float, card: str) -> str:
        amount_cents = int(amount_usd * 100)      # конвертація валюти
        clean_card = card.replace("-", "").replace(" ", "")  # нормалізація картки
        result = self._api.make_payment(amount_cents, clean_card)
        return result["transaction_id"]

# Ваш код знає тільки про PaymentProcessor — не знає про legacy
def process_order(amount: float, card: str, processor: PaymentProcessor) -> str:
    return processor.charge(amount, card)

# Використання
legacy = LegacyPaymentAPI()
adapter = LegacyPaymentAdapter(legacy)
txn_id = process_order(29.99, "4111-1111-1111-1111", adapter)
```

**Де зустрічається:**
- Інтеграція з платіжними системами
- Обгортки для хмарних SDK (boto3, cloudinary) в ваш внутрішній інтерфейс
- `io.StringIO` — адаптує рядок до файлового API

---

## Порівняння

| Паттерн | Проблема | Рішення | Ключова ідея |
|---------|---------|---------|------------|
| Singleton | Потрібен один екземпляр | `__new__` з кешуванням | Контроль кількості екземплярів |
| Factory | Вибір реалізації в runtime | Функція або клас що створює | Розділення "що" від "як" |
| Adapter | Несумісні інтерфейси | Обгортка що перетворює | Дозволяє спілкуватись "різним мовам" |

---

## Ресурси

- [refactoring.guru/uk/design-patterns](https://refactoring.guru/uk/design-patterns) — з ілюстраціями та Python прикладами
- [python-patterns.guide](https://python-patterns.guide) — Python-specific підхід до паттернів
