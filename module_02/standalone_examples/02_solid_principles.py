"""
Модуль 02.2: SOLID принципи
=============================

Що вивчається:
  S — Single Responsibility: один клас = одна причина змінитись
  O — Open/Closed: відкрито для розширення, закрито для модифікації
  L — Liskov Substitution: підклас працює скрізь де батько (з 01_)
  I — Interface Segregation: краще кілька малих інтерфейсів ніж один великий
  D — Dependency Inversion: залежати від абстракцій, не від реалізацій

Запуск: python 02_solid_principles.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol


# ─── S: Single Responsibility ────────────────────────────────────────────────

@dataclass
class User:
    name: str
    email: str


class GodClass:
    """
    ❌ Порушення SRP — три причини змінитись:
       1. Логіка роботи з юзером
       2. Логіка відправки пошти
       3. Логіка збереження в БД
    """
    def create_user(self, name: str, email: str) -> User:
        user = User(name, email)
        # одразу і в БД, і лист
        print(f"[DB] INSERT user {email}")
        print(f"[Email] Sending welcome to {email}")
        return user


class UserService:
    """✓ SRP: тільки бізнес-логіка роботи з юзером."""
    def create(self, name: str, email: str) -> User:
        return User(name, email)


class UserRepository:
    """✓ SRP: тільки збереження."""
    _users: list[User] = []

    def save(self, user: User) -> None:
        self._users.append(user)
        print(f"[DB] Saved: {user.email}")

    def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._users if u.email == email), None)


class EmailService:
    """✓ SRP: тільки відправка пошти."""
    def send_welcome(self, user: User) -> None:
        print(f"[Email] Welcome letter → {user.email}")


# ─── O: Open/Closed ──────────────────────────────────────────────────────────

class Notifier(ABC):
    """Абстракція — закрита для модифікації, відкрита для розширення."""
    @abstractmethod
    def send(self, recipient: str, message: str) -> str: ...


class EmailNotifier(Notifier):
    def send(self, recipient, message):
        return f"[Email] → {recipient}: {message}"


class SMSNotifier(Notifier):
    def send(self, recipient, message):
        return f"[SMS] → {recipient}: {message[:160]}"


# Нова реалізація — не чіпаємо EmailNotifier і SMSNotifier
class SlackNotifier(Notifier):
    def send(self, recipient, message):
        return f"[Slack] @{recipient}: {message}"


def notify_all(notifiers: list[Notifier], recipient: str, message: str) -> None:
    """✓ OCP: код не знає про конкретні типи, не потребує if/elif."""
    for notifier in notifiers:
        print(notifier.send(recipient, message))


# ─── I: Interface Segregation ────────────────────────────────────────────────

class FatWorker(ABC):
    """❌ ISP: Robot змушений реалізовувати eat() якого не потребує."""
    @abstractmethod
    def work(self) -> str: ...
    @abstractmethod
    def eat(self) -> str: ...


class Workable(ABC):
    """✓ ISP: окремий маленький інтерфейс."""
    @abstractmethod
    def work(self) -> str: ...


class Eatable(ABC):
    """✓ ISP: тільки те що потрібно."""
    @abstractmethod
    def eat(self) -> str: ...


class HumanWorker(Workable, Eatable):
    """Людина: і працює, і їсть."""
    def work(self) -> str: return "людина працює"
    def eat(self) -> str: return "людина їсть"


class RobotWorker(Workable):
    """Робот: тільки працює."""
    def work(self) -> str: return "робот працює"


# ─── D: Dependency Inversion ─────────────────────────────────────────────────

class HardCodedService:
    """❌ DIP: жорстко залежить від конкретного EmailNotifier."""
    def __init__(self):
        self._notifier = EmailNotifier()   # не можна замінити без зміни коду

    def process(self, user: str) -> str:
        return self._notifier.send(user, "processed")


class MessageService:
    """
    ✓ DIP: залежить від абстракції Notifier.
    Конкретна реалізація передається через конструктор (Dependency Injection).
    """
    def __init__(self, notifier: Notifier):
        self._notifier = notifier     # будь-яка реалізація Notifier

    def process(self, user: str) -> str:
        return self._notifier.send(user, "processed")


# ─── Демонстрація ─────────────────────────────────────────────────────────────

def demo_srp() -> None:
    print("\n=== S: Single Responsibility ===")
    svc = UserService()
    repo = UserRepository()
    email_svc = EmailService()

    user = svc.create("Alice", "alice@example.com")
    repo.save(user)
    email_svc.send_welcome(user)
    print(f"Знайдено: {repo.find_by_email('alice@example.com')}")


def demo_ocp() -> None:
    print("\n=== O: Open/Closed ===")
    notifiers: list[Notifier] = [
        EmailNotifier(),
        SMSNotifier(),
        SlackNotifier(),  # нова реалізація — код notify_all не змінювався
    ]
    notify_all(notifiers, "bob", "Hello!")


def demo_isp() -> None:
    print("\n=== I: Interface Segregation ===")
    workers: list[Workable] = [HumanWorker(), RobotWorker()]
    for w in workers:
        print(f"  {w.__class__.__name__}.work() → {w.work()}")

    eaters: list[Eatable] = [HumanWorker()]  # Robot не потрапить сюди
    for e in eaters:
        print(f"  {e.__class__.__name__}.eat() → {e.eat()}")


def demo_dip() -> None:
    print("\n=== D: Dependency Inversion ===")

    # Виробничий код — реальний notifier
    prod_service = MessageService(EmailNotifier())
    print(f"  Production: {prod_service.process('alice')}")

    # Тест — замінюємо залежність без зміни MessageService
    class MockNotifier(Notifier):
        def send(self, recipient, message):
            return f"[MOCK] {recipient}: {message}"

    test_service = MessageService(MockNotifier())
    print(f"  Test:       {test_service.process('alice')}")
    print("  ↑ Один і той самий клас, різні залежності")


if __name__ == "__main__":
    demo_srp()
    demo_ocp()
    demo_isp()
    demo_dip()

    print("\n=== Підсумок SOLID ===")
    print("  S: UserService, UserRepository, EmailService — три окремих класи")
    print("  O: notify_all() не змінювався коли додали SlackNotifier")
    print("  L: LSP — дивіться 01_abc_and_oop.py")
    print("  I: RobotWorker реалізує тільки Workable, не Eatable")
    print("  D: MessageService(notifier) — залежність через конструктор")
