"""
Модуль 02.5: Chatbot Demo
==========================

Простий інтерактивний чат-бот що демонструє:
  - Human ABC інтерфейс (з 01_)
  - Factory для різних типів відповідей (з 03_)
  - Singleton для "пам'яті" бота

Команди в боті: walk, run, breathe, help, quit

Запуск: python 05_chatbot_demo.py
"""

from abc import ABC, abstractmethod


# ─── Human інтерфейс (з модуля 01) ───────────────────────────────────────────

class Human(ABC):
    @abstractmethod
    def walk(self) -> str: ...

    @abstractmethod
    def run(self) -> str: ...

    def breathe(self) -> str:
        return "вдих → видих"


class BotPersona(Human):
    """Персонаж бота — реалізує Human через текстові відповіді."""

    def __init__(self, name: str):
        self.name = name

    def walk(self) -> str:
        return f"{self.name} крокує назустріч вам..."

    def run(self) -> str:
        return f"{self.name} мчить на допомогу!"


# ─── Пам'ять бота (Singleton) ────────────────────────────────────────────────

class BotMemory:
    """Singleton: одна пам'ять на весь сеанс розмови."""
    _instance: "BotMemory | None" = None

    def __new__(cls) -> "BotMemory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._history: list[str] = []
            cls._instance._message_count = 0
        return cls._instance

    def remember(self, message: str) -> None:
        self._history.append(message)
        self._message_count += 1

    def get_count(self) -> int:
        return self._message_count

    def get_last(self, n: int = 3) -> list[str]:
        return self._history[-n:]


# ─── Factory для відповідей бота ─────────────────────────────────────────────

class ResponseStyle(ABC):
    @abstractmethod
    def format(self, text: str) -> str: ...


class FriendlyStyle(ResponseStyle):
    def format(self, text: str) -> str:
        return f"😊 {text}"


class FormalStyle(ResponseStyle):
    def format(self, text: str) -> str:
        return f"[Офіційно] {text}."


class ExcitedStyle(ResponseStyle):
    def format(self, text: str) -> str:
        return f"🎉 {text.upper()}!!!"


def create_style(name: str) -> ResponseStyle:
    styles = {
        "friendly": FriendlyStyle,
        "formal":   FormalStyle,
        "excited":  ExcitedStyle,
    }
    cls = styles.get(name, FriendlyStyle)
    return cls()


# ─── Бот ─────────────────────────────────────────────────────────────────────

class Chatbot:
    """
    Збирає всі паттерни разом:
      - persona: Human (ABC + поліморфізм)
      - memory: BotMemory (Singleton)
      - style: ResponseStyle (Factory)
    """

    COMMANDS = {
        "walk":    "побачити як бот ходить",
        "run":     "побачити як бот біжить",
        "breathe": "нагадати боту дихати",
        "style":   "змінити стиль (friendly/formal/excited)",
        "history": "переглянути останні 3 повідомлення",
        "help":    "показати цю допомогу",
        "quit":    "вийти",
    }

    def __init__(self, name: str = "РОБА", style: str = "friendly"):
        self.persona = BotPersona(name)
        self.memory = BotMemory()
        self.style = create_style(style)

    def _reply(self, text: str) -> str:
        response = self.style.format(text)
        self.memory.remember(f"бот: {response}")
        return response

    def handle(self, command: str) -> str:
        command = command.strip().lower()
        self.memory.remember(f"user: {command}")

        if command == "walk":
            return self._reply(self.persona.walk())

        elif command == "run":
            return self._reply(self.persona.run())

        elif command == "breathe":
            return self._reply(f"Дихаю: {self.persona.breathe()}")

        elif command.startswith("style "):
            style_name = command.split(" ", 1)[1]
            self.style = create_style(style_name)
            return self._reply(f"Стиль змінено на '{style_name}'")

        elif command == "history":
            last = self.memory.get_last()
            if not last:
                return self._reply("Поки що немає історії")
            lines = "\n  ".join(last)
            return self._reply(f"Останні повідомлення:\n  {lines}")

        elif command == "help":
            lines = "\n  ".join(
                f"{cmd:10} — {desc}" for cmd, desc in self.COMMANDS.items()
            )
            return f"Команди:\n  {lines}"

        elif command in ("quit", "exit", "q"):
            count = self.memory.get_count()
            return self._reply(f"До побачення! Всього повідомлень: {count}")

        else:
            return self._reply(
                f"Не знаю команди '{command}'. Введіть 'help' для довідки"
            )


# ─── Запуск ──────────────────────────────────────────────────────────────────

def main() -> None:
    bot = Chatbot(name="РОБА", style="friendly")

    print("╔══════════════════════════════════╗")
    print("║  Chatbot Demo  —  Module 02      ║")
    print("║  Введіть 'help' для списку команд ║")
    print("║  Введіть 'quit' для виходу       ║")
    print("╚══════════════════════════════════╝\n")

    while True:
        try:
            user_input = input("Ви: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not user_input:
            continue

        response = bot.handle(user_input)
        print(f"Бот: {response}\n")

        if user_input.lower() in ("quit", "exit", "q"):
            break


if __name__ == "__main__":
    main()
