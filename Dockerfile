FROM python:3.11-slim

WORKDIR /app

# Встановити системні залежності
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копіювати файл залежностей
COPY requirements.txt .

# Встановити Python залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіювати код проекту
COPY . .

# Команда за замовчуванням
CMD ["python", "--version"]
