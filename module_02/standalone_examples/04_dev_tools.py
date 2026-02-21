"""
Модуль 02.4: Dev Tools — pipenv, poetry, pip
=============================================

Цей скрипт генерує файли конфігурацій для трьох підходів до управління
залежностями Python. Запустіть — отримаєте pyproject.toml, Pipfile,
requirements.txt у поточній директорії.

Запуск: python 04_dev_tools.py

Що генерується:
  pyproject.toml   ← poetry
  Pipfile          ← pipenv
  requirements.txt ← pip
"""

import sys
from pathlib import Path


# ─── Шаблони файлів ──────────────────────────────────────────────────────────

PYPROJECT_TOML = '''[tool.poetry]
name = "chatbot-demo"
version = "0.1.0"
description = "Chatbot demo using Human interface"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''

PIPFILE = '''[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]

[dev-packages]
pytest = "*"

[requires]
python_version = "3.11"
'''

REQUIREMENTS_TXT = '''# Production dependencies
# Generated manually (or: pip freeze > requirements.txt)
# Tip: pin versions to avoid "works on my machine" problems

# No external dependencies for this demo
# Add packages here, e.g.:
# requests==2.32.3
# fastapi==0.115.0
'''

REQUIREMENTS_DEV_TXT = '''# Development dependencies (not needed in production)
-r requirements.txt

pytest==8.3.3
'''


# ─── Пояснення командного інтерфейсу ─────────────────────────────────────────

COMMANDS_GUIDE = """
┌─────────────────────────────────────────────────────────────┐
│          ПОРІВНЯННЯ ІНСТРУМЕНТІВ УПРАВЛІННЯ ЗАЛЕЖНОСТЯМИ     │
└─────────────────────────────────────────────────────────────┘

━━━ pip + requirements.txt ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  python -m venv .venv               # створити virtual env
  source .venv/bin/activate          # Linux/Mac
  .venv\\Scripts\\activate             # Windows

  pip install requests               # встановити пакет
  pip install -r requirements.txt    # встановити все з файлу
  pip freeze > requirements.txt      # зберегти поточні версії
  pip list --outdated                # перевірити застарілі

  Мінус: requirements.txt включає транзитивні залежності.
  Мінус: немає поділу prod/dev залежностей в одному файлі.

━━━ pipenv ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  pip install pipenv                 # один раз глобально
  pipenv install requests            # встановити + додати до Pipfile
  pipenv install pytest --dev        # dev-залежність
  pipenv shell                       # активувати virtual env
  pipenv run python bot.py           # запустити без активації
  pipenv lock                        # оновити Pipfile.lock
  pipenv install                     # відтворити з Pipfile.lock

  Плюс: автоматичний virtual env, Pipfile.lock для відтворюваності.
  Мінус: повільніший за pip, менш активно підтримується.

━━━ poetry ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  pip install poetry                 # один раз глобально
  poetry new my-project              # новий проект з структурою
  poetry init                        # ініціалізація в існуючому

  poetry add requests                # встановити + додати до pyproject.toml
  poetry add pytest --group dev      # dev-залежність
  poetry install                     # відтворити з poetry.lock
  poetry shell                       # активувати virtual env
  poetry run python bot.py           # запустити без активації
  poetry build                       # зібрати пакет для PyPI
  poetry publish                     # опублікувати на PyPI

  Плюс: найкращий UX, інтеграція з PyPI, чистий pyproject.toml.
  Мінус: трохи повільніший ніж pip, потрібно вчити ще один інструмент.

━━━ Коли що використовувати ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  pip + requirements.txt  →  простий скрипт, навчальний проект
  pipenv                  →  якщо проект вже на pipenv або так каже команда
  poetry                  →  новий проект, бібліотека для PyPI, Module 10+

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Як генерувати requirements.txt з poetry/pipenv:

  # poetry
  poetry export -f requirements.txt --output requirements.txt --without-hashes

  # pipenv
  pipenv requirements > requirements.txt
"""


# ─── Головна логіка ──────────────────────────────────────────────────────────

def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"  Створено: {path}")


def main() -> None:
    output_dir = Path(".")

    print("Генерація файлів конфігурацій залежностей...")
    write_file(output_dir / "pyproject.toml", PYPROJECT_TOML)
    write_file(output_dir / "Pipfile", PIPFILE)
    write_file(output_dir / "requirements.txt", REQUIREMENTS_TXT)
    write_file(output_dir / "requirements-dev.txt", REQUIREMENTS_DEV_TXT)

    print(COMMANDS_GUIDE)

    print("\nСтруктура python-проекту (рекомендована для web-додатків):")
    print("""
  my_project/
  ├── pyproject.toml      ← poetry (або Pipfile для pipenv)
  ├── requirements.txt    ← для Dockerfile / Render.com
  ├── requirements-dev.txt← тільки для розробки
  ├── .env.example        ← шаблон змінних середовища (без секретів!)
  ├── .gitignore          ← .env, .venv, __pycache__, *.pyc
  ├── README.md
  └── src/
      └── main.py
""")


if __name__ == "__main__":
    main()
