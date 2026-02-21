# OOP, ABC та SOLID

---

## ABC — Abstract Base Classes

### Навіщо?

Python — duck typing: якщо об'єкт має метод `walk()`, неважливо від якого класу він.
Але в команді з 5+ людей duck typing стає проблемою:

```python
# Без ABC — помилка видна лише під час виклику
class Person:
    pass  # забули walk()

p = Person()
p.walk()  # AttributeError: 'Person' object has no attribute 'walk'
           # Ця помилка може виникнути в production, не при написанні коду
```

```python
# З ABC — помилка одразу при інстанціюванні
from abc import ABC, abstractmethod

class Human(ABC):
    @abstractmethod
    def walk(self) -> str: ...

class Person(Human):
    pass  # НЕ реалізували walk()

p = Person()  # TypeError: Can't instantiate abstract class Person
              # Ця помилка виникає відразу, до будь-якого виклику
```

### Структура

```python
class Human(ABC):
    # Абстрактний метод — МАЮТЬ реалізувати підкласи
    @abstractmethod
    def walk(self) -> str: ...

    @abstractmethod
    def run(self) -> str: ...

    # Конкретний метод — підкласи УСПАДКОВУЮТЬ, не обов'язково перевизначати
    def breathe(self) -> str:
        return "inhale → exhale"
```

### Ієрархія

```
Human (ABC)
├── walk()    ← abstract
├── run()     ← abstract
└── breathe() ← concrete

Person(Human)
├── walk() → "walking on two legs"
└── run()  → "running fast"

Child(Human)
├── walk() → "toddling"
└── run()  → ??? (LSP issue — see below)
```

---

## LSP — Liskov Substitution Principle

Підклас повинен працювати всюди де очікується батьківський клас.

### Порушення (❌)

```python
class Child(Human):
    def walk(self) -> str:
        return "toddling"

    def run(self) -> str:
        raise NotImplementedError("Children can't run yet!")
        # Порушення LSP! Якщо хтось очікує Human і викликає run() —
        # для Child отримає виключення, хоча для Person все ок
```

### Правильно (✓)

**Варіант 1:** Child може бігати — просто повільніше

```python
class Child(Human):
    def run(self) -> str:
        return "running clumsily"  # Те саме API, різна поведінка — OK
```

**Варіант 2:** Розділити інтерфейси (ISP + LSP)

```python
class Walkable(ABC):
    @abstractmethod
    def walk(self) -> str: ...

class Runnable(ABC):
    @abstractmethod
    def run(self) -> str: ...

class Adult(Walkable, Runnable):  # дорослий може і ходити, і бігати
    ...

class Toddler(Walkable):          # дитина поки тільки ходить
    ...
```

---

## SOLID — усі 5 принципів

### S — Single Responsibility Principle

Клас повинен мати лише одну причину для зміни.

```python
# ❌ God class — три причини змінитись
class UserManager:
    def create_user(self, data): ...
    def send_welcome_email(self, user): ...   # логіка email
    def save_to_database(self, user): ...     # логіка БД

# ✓ Розділено
class UserService:
    def create_user(self, data): ...          # тільки бізнес-логіка

class EmailService:
    def send_welcome(self, user): ...         # тільки email

class UserRepository:
    def save(self, user): ...                 # тільки БД
```

### O — Open/Closed Principle

Відкрито для розширення, закрито для модифікації.

```python
# ❌ Потрібно змінювати код при кожному новому каналі
def send_notification(user, message, type):
    if type == "email":
        send_email(user.email, message)
    elif type == "sms":
        send_sms(user.phone, message)
    # Щоб додати push — треба редагувати цей метод

# ✓ Новий канал = новий клас, без зміни існуючого коду
class Notifier(ABC):
    @abstractmethod
    def send(self, user, message): ...

class EmailNotifier(Notifier):
    def send(self, user, message):
        send_email(user.email, message)

class SMSNotifier(Notifier):
    def send(self, user, message):
        send_sms(user.phone, message)

# Додаємо Push — не чіпаємо EmailNotifier і SMSNotifier
class PushNotifier(Notifier):
    def send(self, user, message):
        send_push(user.device_token, message)
```

### L — Liskov Substitution (детально вище)

### I — Interface Segregation Principle

Клієнт не повинен залежати від методів які він не використовує.

```python
# ❌ Жирний інтерфейс
class Worker(ABC):
    @abstractmethod
    def work(self) -> str: ...
    @abstractmethod
    def eat(self) -> str: ...   # роботи не їдять!

class Robot(Worker):
    def work(self): return "working"
    def eat(self): raise NotImplementedError("Robots don't eat")  # порушення LSP!

# ✓ Розділені інтерфейси
class Workable(ABC):
    @abstractmethod
    def work(self) -> str: ...

class Eatable(ABC):
    @abstractmethod
    def eat(self) -> str: ...

class Human(Workable, Eatable):
    def work(self): return "working"
    def eat(self): return "eating"

class Robot(Workable):           # тільки те що потрібно
    def work(self): return "working"
```

### D — Dependency Inversion Principle

Залежати від абстракцій, а не від конкретних реалізацій.

```python
# ❌ Жорстка залежність — важко тестувати
class MessageService:
    def __init__(self):
        self.sender = EmailSender()  # жорстко вшито, не замінити в тестах

# ✓ Залежність через конструктор (Dependency Injection)
class MessageService:
    def __init__(self, sender: Notifier):  # ABC, не конкретний клас
        self.sender = sender

# Виробничий код
service = MessageService(EmailNotifier())

# Тест
mock_sender = MockNotifier()
service = MessageService(mock_sender)  # легко замінити
```

---

## Що Junior має знати про паттерни

| Рівень | Що знати |
|--------|---------|
| Junior | Singleton, Factory, Adapter — розпізнати і пояснити |
| Middle | Observer, Strategy, Decorator — реалізувати |
| Senior | Коли паттерн шкодить (overengineering) |

Повний список: [refactoring.guru/uk/design-patterns](https://refactoring.guru/uk/design-patterns)
