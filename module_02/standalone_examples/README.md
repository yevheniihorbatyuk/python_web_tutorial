# Standalone Examples — Module 02

Кожен файл є незалежним і запускається окремо.

| # | Файл | Тема | Потребує |
|---|------|------|---------|
| 01 | `01_abc_and_oop.py` | ABC, Human/Person/Child, LSP | Нічого |
| 02 | `02_solid_principles.py` | Усі 5 SOLID принципів | Нічого |
| 03 | `03_design_patterns.py` | Singleton, Factory, Adapter | Нічого |
| 04 | `04_dev_tools.py` | pipenv/poetry/pip; генерує конфіги | Нічого |
| 05 | `05_chatbot_demo.py` | Інтерактивний чат-бот | Нічого |
| 06 | `06_docker_intro.py` | Dockerfile + Docker команди | Нічого (Docker — опційно) |

## Швидкий старт

```bash
# Всі приклади — самодостатні
python 01_abc_and_oop.py
python 02_solid_principles.py
python 03_design_patterns.py

# Генерує конфігураційні файли
python 04_dev_tools.py

# Інтерактивний бот (Ctrl+C або 'quit' для виходу)
python 05_chatbot_demo.py

# Генерує Dockerfile
python 06_docker_intro.py > Dockerfile
# потім:
# docker build -t chatbot .
# docker run -it chatbot
```
