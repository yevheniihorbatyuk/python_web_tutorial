"""
Модуль 02.3: Design Patterns для Junior
=========================================

Три паттерни що ви зустрінете в перший місяць роботи:
  1. Singleton  — один екземпляр на весь додаток (пул з'єднань до БД)
  2. Factory    — вибір реалізації без зміни клієнтського коду
  3. Adapter    — обгортка для несумісного інтерфейсу

Запуск: python 03_design_patterns.py
"""

from abc import ABC, abstractmethod


# ─── 1. Singleton ─────────────────────────────────────────────────────────────

class DatabaseConnection:
    """
    Singleton для з'єднання з базою даних.

    Реальна СУБД може підтримувати обмежену кількість з'єднань.
    Singleton гарантує що пул створюється один раз.
    """
    _instance: "DatabaseConnection | None" = None

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connected = False
            cls._instance._url = ""
        return cls._instance

    def connect(self, url: str) -> None:
        if not self._connected:
            print(f"[DB] Підключення до {url}...")
            self._connected = True
            self._url = url
        else:
            print(f"[DB] Вже підключено до {self._url}, ігноруємо повторний виклик")

    def execute(self, sql: str) -> list:
        if not self._connected:
            raise RuntimeError("Спочатку викличте connect()")
        print(f"[DB] Виконую: {sql}")
        return []

    def disconnect(self) -> None:
        if self._connected:
            print(f"[DB] Відключення від {self._url}")
            self._connected = False


# ─── 2. Factory ───────────────────────────────────────────────────────────────

class BotResponse(ABC):
    """Базовий клас відповіді бота — Factory Product."""
    @abstractmethod
    def format(self, text: str) -> str: ...


class PlainResponse(BotResponse):
    def format(self, text: str) -> str:
        return text


class UpperCaseResponse(BotResponse):
    """Для відповідей де треба кричати :)"""
    def format(self, text: str) -> str:
        return text.upper()


class EmojiResponse(BotResponse):
    def format(self, text: str) -> str:
        return f"🤖 {text} ✨"


class BotResponseFactory:
    """
    Factory: клієнт каже ЩО хоче, factory знає ЯК створити.
    OCP: новий тип відповіді = нова реєстрація, код клієнта не змінюється.
    """
    _registry: dict[str, type[BotResponse]] = {
        "plain":   PlainResponse,
        "shout":   UpperCaseResponse,
        "emoji":   EmojiResponse,
    }

    @classmethod
    def register(cls, name: str, response_cls: type[BotResponse]) -> None:
        """Реєстрація нового типу відповіді без зміни factory."""
        cls._registry[name] = response_cls

    @classmethod
    def create(cls, style: str) -> BotResponse:
        response_cls = cls._registry.get(style)
        if response_cls is None:
            available = ", ".join(cls._registry)
            raise ValueError(f"Стиль '{style}' невідомий. Доступні: {available}")
        return response_cls()

    @classmethod
    def available_styles(cls) -> list[str]:
        return list(cls._registry)


# ─── 3. Adapter ──────────────────────────────────────────────────────────────

class LegacyTranslatorAPI:
    """
    Стара бібліотека перекладів з незручним інтерфейсом.
    Не можна змінити (стороння залежність / legacy код).
    """
    def translate_text(
        self,
        text: str,
        source_lang_code: str,
        target_lang_code: str,
        use_formal: bool = False,
    ) -> dict:
        """Повертає dict з полем 'translated_text' та метаданими."""
        # Імітація перекладу
        mock_translations = {
            ("en", "uk"): {"hello": "привіт", "world": "світ", "bot": "бот"},
            ("uk", "en"): {"привіт": "hello", "світ": "world", "бот": "bot"},
        }
        words = text.lower().split()
        mapping = mock_translations.get((source_lang_code, target_lang_code), {})
        translated = " ".join(mapping.get(w, w) for w in words)
        return {
            "translated_text": translated,
            "source": source_lang_code,
            "target": target_lang_code,
            "formal": use_formal,
        }


class Translator(ABC):
    """Новий зручний інтерфейс перекладача у вашому додатку."""
    @abstractmethod
    def translate(self, text: str, to_language: str) -> str: ...


class TranslatorAdapter(Translator):
    """
    Adapter: перетворює інтерфейс LegacyTranslatorAPI
    у зручний Translator.

    Клієнтський код знає тільки про Translator — не знає про Legacy.
    """
    _LANG_CODES = {"ukrainian": "uk", "english": "en", "german": "de"}

    def __init__(self, legacy_api: LegacyTranslatorAPI, from_language: str = "english"):
        self._api = legacy_api
        self._source = self._LANG_CODES.get(from_language, from_language)

    def translate(self, text: str, to_language: str) -> str:
        target = self._LANG_CODES.get(to_language, to_language)
        result = self._api.translate_text(
            text=text,
            source_lang_code=self._source,
            target_lang_code=target,
            use_formal=False,
        )
        return result["translated_text"]


# ─── Демонстрація ─────────────────────────────────────────────────────────────

def demo_singleton() -> None:
    print("=== Singleton ===")
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    print(f"  db1 is db2: {db1 is db2}")  # True

    db1.connect("postgresql://localhost/mydb")
    db2.connect("postgresql://other/db")    # ігнорується — вже підключено
    db1.execute("SELECT 1")
    db1.disconnect()


def demo_factory() -> None:
    print("\n=== Factory ===")
    message = "Привіт, я бот!"

    for style in BotResponseFactory.available_styles():
        response = BotResponseFactory.create(style)
        print(f"  [{style:6}] {response.format(message)}")

    # Реєструємо новий тип — без зміни factory
    class QuotedResponse(BotResponse):
        def format(self, text: str) -> str:
            return f'"{text}"'

    BotResponseFactory.register("quoted", QuotedResponse)
    resp = BotResponseFactory.create("quoted")
    print(f"  [quoted] {resp.format(message)}")


def demo_adapter() -> None:
    print("\n=== Adapter ===")
    legacy = LegacyTranslatorAPI()
    translator: Translator = TranslatorAdapter(legacy, from_language="english")

    text = "hello world"
    translated = translator.translate(text, to_language="ukrainian")
    print(f"  '{text}' → '{translated}'")

    # Зворотній переклад
    back = TranslatorAdapter(legacy, from_language="ukrainian")
    original = back.translate("привіт світ", to_language="english")
    print(f"  'привіт світ' → '{original}'")
    print("  ↑ Клієнтський код не знає про LegacyTranslatorAPI")


if __name__ == "__main__":
    demo_singleton()
    demo_factory()
    demo_adapter()
