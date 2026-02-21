"""
Модуль 02.1: ABC та основи OOP
================================

Що вивчається:
  1. Абстрактний базовий клас (ABC) — Python-інтерфейс
  2. abstractmethod vs конкретний метод
  3. LSP (Liskov Substitution Principle) — порушення та виправлення
  4. Чому ABC кращий за duck typing у командному коді

Запуск: python 01_abc_and_oop.py
"""

from abc import ABC, abstractmethod


# ─── Інтерфейс Human ─────────────────────────────────────────────────────────

class Human(ABC):
    """
    Абстрактний базовий клас — визначає контракт для всіх людей.

    Підкласи МАЮТЬ реалізувати walk() та run().
    breathe() — конкретний метод, успадковується автоматично.
    """

    @abstractmethod
    def walk(self) -> str:
        """Як ця людина ходить."""
        ...

    @abstractmethod
    def run(self) -> str:
        """Як ця людина бігає."""
        ...

    def breathe(self) -> str:
        """Конкретний метод — однаковий для всіх людей."""
        return "вдих → видих"

    def describe(self) -> str:
        """Використовує абстрактні методи через self — поліморфізм."""
        return (
            f"{self.__class__.__name__}: "
            f"іде ({self.walk()}), "
            f"біжить ({self.run()}), "
            f"дихає ({self.breathe()})"
        )


# ─── Коректні реалізації ──────────────────────────────────────────────────────

class Person(Human):
    """Дорослий — повністю реалізує контракт."""

    def walk(self) -> str:
        return "крок за кроком"

    def run(self) -> str:
        return "швидко біжить"


class Athlete(Human):
    """Спортсмен — теж реалізує контракт, але інакше."""

    def __init__(self, sport: str):
        self.sport = sport

    def walk(self) -> str:
        return f"спортивна хода ({self.sport})"

    def run(self) -> str:
        return f"спринт ({self.sport})"


# ─── LSP: порушення ───────────────────────────────────────────────────────────

class ChildBroken(Human):
    """
    НЕПРАВИЛЬНО — порушення LSP (Liskov Substitution Principle).

    ChildBroken не може замінити Human скрізь де очікується Human,
    бо run() кидає виключення замість повернення рядка.
    """

    def walk(self) -> str:
        return "тупотить ніжками"

    def run(self) -> str:
        # ❌ Порушення LSP: клієнт очікує str, отримає RuntimeError
        raise RuntimeError("Маленькі діти не можуть бігати!")


# ─── LSP: правильне рішення ───────────────────────────────────────────────────

class Child(Human):
    """
    ПРАВИЛЬНО — контракт виконано, поведінка інша але API однакове.
    Дитина може бігати — просто незграбно. Це нормальна LSP-сумісна поведінка.
    """

    def walk(self) -> str:
        return "тупотить ніжками"

    def run(self) -> str:
        return "біжить незграбно"  # ✓ повертає str, як і очікує контракт


# ─── Демонстрація ─────────────────────────────────────────────────────────────

def demonstrate_polymorphism(humans: list[Human]) -> None:
    """
    Ця функція очікує список Human.
    Вона НЕ знає і НЕ повинна знати, які саме підкласи передані.
    Це і є суть поліморфізму.
    """
    print("\n--- Поліморфізм: одна функція, різні реалізації ---")
    for human in humans:
        print(f"  {human.describe()}")


def show_lsp_violation() -> None:
    """Демонструє чому LSP-порушення небезпечне."""
    print("\n--- LSP: порушення ---")
    humans: list[Human] = [Person(), ChildBroken()]
    for human in humans:
        try:
            print(f"  {human.__class__.__name__}.run() → {human.run()}")
        except RuntimeError as e:
            print(f"  {human.__class__.__name__}.run() → ПОМИЛКА: {e}")
    print("  ↑ Якщо ChildBroken використовується де очікується Human — баг!")


def show_lsp_correct() -> None:
    """Демонструє правильну LSP-сумісну ієрархію."""
    print("\n--- LSP: правильно ---")
    humans: list[Human] = [Person(), Child(), Athlete("марафон")]
    for human in humans:
        print(f"  {human.__class__.__name__}.run() → {human.run()}")
    print("  ↑ Будь-який Human можна підставити — код не ламається")


def show_abc_protection() -> None:
    """Показує що ABC захищає від неповної реалізації."""
    print("\n--- ABC: захист від неповної реалізації ---")

    class Incomplete(Human):
        def walk(self) -> str:
            return "хода"
        # run() НЕ реалізовано

    try:
        obj = Incomplete()
    except TypeError as e:
        print(f"  Спроба створити Incomplete() → TypeError: {e}")
        print("  ↑ ABC зупиняє помилку одразу, не пізніше під час виклику")


if __name__ == "__main__":
    demonstrate_polymorphism([
        Person(),
        Child(),
        Athlete("плавання"),
    ])

    show_lsp_violation()
    show_lsp_correct()
    show_abc_protection()

    # Breathe — конкретний метод, без перевизначення
    print(f"\nPerson().breathe() → {Person().breathe()}")
    print(f"Child().breathe()  → {Child().breathe()}")
    print("↑ Обидва успадкували один метод")
