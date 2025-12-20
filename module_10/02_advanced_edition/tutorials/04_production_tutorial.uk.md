# Туторіал: Патерни для продакшну та моніторинг

**Мета**: застосувати готові до продакшну патерни, такі як кешування та обмеження швидкості, до вашого інтегрованого додатку для скрапінгу.

---

## Крок 1: Впровадження кешування

Ми додамо кешування до представлення Django, яке обслуговує зібрані дані.

1.  **Налаштуйте Django для кешування Redis.** Відкрийте `settings.py` та додайте налаштування `CACHES`:
    ```python
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1", # Використовуйте іншу БД, ніж Celery
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
    ```
    Можливо, вам доведеться встановити `django-redis`: `pip install django-redis`.

2.  **Створіть кешоване представлення.** У `django_integration/views.py` створіть представлення для обслуговування цитат, яке використовує патерн cache-aside.
    ```python
    from django.core.cache import cache
    from django.http import JsonResponse
    from .models import Quote

    def cached_quote_list(request):
        cache_key = "all_quotes"
        quotes = cache.get(cache_key)
        
        if quotes is None:
            # Промах кешу: отримати з БД, потім встановити кеш
            quotes = list(Quote.objects.values('text', 'author__name'))
            cache.set(cache_key, quotes, timeout=60 * 15) # Кешувати на 15 хвилин
            print("Промах кешу - отримано з БД.")
        else:
            print("Попадання в кеш!")
            
        return JsonResponse(quotes, safe=False)
    ```

3.  **Додайте URL** для цього представлення та протестуйте його. Зверніться до ендпоінту кілька разів; ви повинні побачити "Промах кешу" лише під час першого запиту.

---

## Крок 2: Впровадження обмеження швидкості

Ми створимо простий обмежувач швидкості за допомогою Redis для захисту ендпоінту API.

1.  **Створіть утиліту обмежувача швидкості** у `code/utils/rate_limiter.py`.
    ```python
    import redis
    from datetime import timedelta

    client = redis.Redis(host='localhost', port=6379, db=2)

    def is_rate_limited(key: str, limit: int, period: timedelta):
        """
        Повертає True, якщо ключ обмежений за швидкістю, інакше False.
        """
        if client.setnx(key, limit):
            client.expire(key, int(period.total_seconds()))
        
        bucket_val = client.get(key)
        if bucket_val and int(bucket_val) > 0:
            client.decrby(key, 1)
            return False
        
        return True
    ```

2.  **Застосуйте обмежувач швидкості у представленні.**
    ```python
    from .utils.rate_limiter import is_rate_limited
    from datetime import timedelta

    def protected_view(request):
        # Обмежити до 10 запитів на хвилину на IP
        ip_address = request.META.get('REMOTE_ADDR')
        key = f"rate_limit:{ip_address}"
        
        if is_rate_limited(key, limit=10, period=timedelta(minutes=1)):
            return JsonResponse({'error': 'Перевищено ліміт запитів'}, status=429)
            
        return JsonResponse({'message': 'Успіх'})
    ```

---

## Крок 3: Налаштування структурованого логування

Ми налаштуємо Django для виводу логів у форматі JSON.

1.  **Встановіть `python-json-logger`**:
    ```bash
    pip install python-json-logger
    ```
2.  **Налаштуйте `LOGGING` у `settings.py`**:
    ```python
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
            'my_app': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }
    ```

3.  **Використовуйте логер з додатковим контекстом**:
    ```python
    import logging
    logger = logging.getLogger(__name__)

    def my_view(request):
        logger.info("Користувач відвідав сторінку.", extra={
            'user_id': request.user.id,
            'path': request.path,
        })
        # ...
    ```
    Коли ви запустите свій сервер, ви тепер побачите логи, відформатовані як об'єкти JSON.
