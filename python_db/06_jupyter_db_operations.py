# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Модуль 6.6: Аналіз Даних з PostgreSQL та Pandas
#
# Цей notebook демонструє:
# - Підключення до PostgreSQL
# - Завантаження даних у pandas DataFrame
# - Аналіз даних
# - RFM сегментація клієнтів
# - Візуалізація (опціонально)

# %% [markdown]
# ## 1. Підготовка та Підключення

# %%
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Опціонально: візуалізація
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("whitegrid")
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib не встановлено. Візуалізація недоступна.")

# %%
from python_web_tutorial.utils.db import DatabaseConfig, get_connection

# Конфігурація підключення з єдиного джерела правди
db_config = DatabaseConfig()
conn = get_connection(db_config)
print("✅ Підключення до PostgreSQL успішне!")

# %% [markdown]
# ## 2. Завантаження Даних

# %%
# Функція для завантаження даних у DataFrame
def load_data(query):
    """Завантажити дані з PostgreSQL у pandas DataFrame"""
    return pd.read_sql_query(query, conn)

# %%
# Завантажити основні таблиці
customers_df = load_data("SELECT * FROM customers")
orders_df = load_data("SELECT * FROM orders")
products_df = load_data("SELECT * FROM products")
order_items_df = load_data("SELECT * FROM order_items")

print(f"📊 Завантажено даних:")
print(f"  Клієнтів: {len(customers_df)}")
print(f"  Замовлень: {len(orders_df)}")
print(f"  Товарів: {len(products_df)}")
print(f"  Позицій замовлень: {len(order_items_df)}")

# %% [markdown]
# ## 3. Базовий Аналіз Даних

# %%
# 3.1 Перегляд даних клієнтів
print("👥 Клієнти:")
customers_df.head()

# %%
# 3.2 Статистика по містах
print("📍 Розподіл клієнтів по містах:")
city_stats = customers_df['city'].value_counts()
print(city_stats)

# %%
# 3.3 Аналіз замовлень
print("📦 Статистика замовлень:")
print(f"Загальна кількість: {len(orders_df)}")
print(f"Загальна сума: {orders_df['total_amount'].sum():.2f} грн")
print(f"Середнє замовлення: {orders_df['total_amount'].mean():.2f} грн")
print(f"\nСтатуси замовлень:")
print(orders_df['status'].value_counts())

# %% [markdown]
# ## 4. Складний Аналіз з JOIN

# %%
# 4.1 Об'єднати дані про клієнтів та їх замовлення
query = """
SELECT
    c.id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.city,
    c.registration_date,
    COUNT(o.id) AS order_count,
    COALESCE(SUM(o.total_amount), 0) AS total_spent,
    COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name, c.city, c.registration_date
"""

customer_analysis = load_data(query)
print("🔍 Аналіз клієнтів:")
customer_analysis.head(10)

# %%
# 4.2 Топ-10 клієнтів за сумою покупок
print("💰 Топ-10 клієнтів:")
top_customers = customer_analysis.nlargest(10, 'total_spent')
top_customers[['customer_name', 'city', 'order_count', 'total_spent']]

# %% [markdown]
# ## 5. RFM Аналіз (Recency, Frequency, Monetary)

# %%
# RFM - модель сегментації клієнтів
# R - Recency (як давно купляв)
# F - Frequency (як часто купляє)
# M - Monetary (скільки витрачає)

# Розрахувати RFM метрики
rfm_query = """
SELECT
    c.id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    MAX(o.order_date) AS last_order_date,
    COUNT(o.id) AS frequency,
    SUM(o.total_amount) AS monetary,
    CURRENT_DATE - MAX(o.order_date)::DATE AS recency_days
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name, c.email
"""

rfm_df = load_data(rfm_query)

# Створити RFM оцінки (1-5, де 5 - найкраще)
rfm_df['R_score'] = pd.qcut(rfm_df['recency_days'], 5, labels=[5,4,3,2,1], duplicates='drop')
rfm_df['F_score'] = pd.qcut(rfm_df['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5], duplicates='drop')
rfm_df['M_score'] = pd.qcut(rfm_df['monetary'], 5, labels=[1,2,3,4,5], duplicates='drop')

# Загальний RFM score
rfm_df['RFM_score'] = (rfm_df['R_score'].astype(int) +
                        rfm_df['F_score'].astype(int) +
                        rfm_df['M_score'].astype(int))

# Сегментація клієнтів
def rfm_segment(row):
    if row['RFM_score'] >= 12:
        return 'VIP'
    elif row['RFM_score'] >= 9:
        return 'Loyal'
    elif row['RFM_score'] >= 6:
        return 'Potential'
    else:
        return 'At Risk'

rfm_df['segment'] = rfm_df.apply(rfm_segment, axis=1)

print("🎯 RFM Сегментація:")
print(rfm_df.groupby('segment').size())

# %%
# Детальна інформація по сегментах
print("\n📊 Детальна статистика по сегментах:")
segment_stats = rfm_df.groupby('segment').agg({
    'recency_days': 'mean',
    'frequency': 'mean',
    'monetary': 'mean'
}).round(2)
segment_stats

# %% [markdown]
# ## 6. Аналіз Товарів

# %%
# 6.1 Топ товари за виручкою
query = """
SELECT
    p.id,
    p.name,
    p.price,
    COUNT(oi.id) AS times_ordered,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.subtotal) AS total_revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name, p.price
ORDER BY total_revenue DESC
LIMIT 10
"""

top_products = load_data(query)
print("🏆 Топ-10 товарів за виручкою:")
top_products

# %%
# 6.2 Аналіз по категоріях
query = """
SELECT
    c.name AS category,
    COUNT(DISTINCT p.id) AS product_count,
    COUNT(oi.id) AS orders_count,
    SUM(oi.subtotal) AS total_revenue,
    AVG(p.price) AS avg_price
FROM categories c
JOIN products p ON c.id = p.category_id
LEFT JOIN order_items oi ON p.id = oi.product_id
GROUP BY c.id, c.name
ORDER BY total_revenue DESC
"""

category_analysis = load_data(query)
print("📦 Аналіз по категоріях:")
category_analysis

# %% [markdown]
# ## 7. Часовий Аналіз

# %%
# 7.1 Продажі по днях
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
orders_df['order_day'] = orders_df['order_date'].dt.date

daily_sales = orders_df.groupby('order_day').agg({
    'id': 'count',
    'total_amount': 'sum'
}).rename(columns={'id': 'orders', 'total_amount': 'revenue'})

print("📈 Продажі по днях:")
print(daily_sales)

# %%
# 7.2 Trend аналіз
print(f"\n📊 Загальна статистика:")
print(f"  Середній дохід на день: {daily_sales['revenue'].mean():.2f} грн")
print(f"  Середня кількість замовлень: {daily_sales['orders'].mean():.1f}")
print(f"  Максимальний дохід за день: {daily_sales['revenue'].max():.2f} грн")

# %% [markdown]
# ## 8. Візуалізація (опціонально)

# %%
if HAS_MATPLOTLIB:
    # 8.1 Розподіл клієнтів по містах
    plt.figure(figsize=(10, 6))
    city_stats.plot(kind='bar', color='skyblue')
    plt.title('Розподіл клієнтів по містах')
    plt.xlabel('Місто')
    plt.ylabel('Кількість клієнтів')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # 8.2 RFM сегменти
    plt.figure(figsize=(8, 6))
    rfm_df['segment'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['gold', 'lightblue', 'lightgreen', 'salmon'])
    plt.title('Розподіл клієнтів по RFM сегментах')
    plt.ylabel('')
    plt.tight_layout()
    plt.show()

    # 8.3 Продажі по днях
    plt.figure(figsize=(12, 6))
    plt.plot(daily_sales.index, daily_sales['revenue'], marker='o', linewidth=2)
    plt.title('Динаміка продажів')
    plt.xlabel('Дата')
    plt.ylabel('Виручка (грн)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
else:
    print("ℹ️  Для візуалізації встановіть: pip install matplotlib seaborn")

# %% [markdown]
# ## 9. Експорт Результатів

# %%
# Зберегти результати аналізу
rfm_df.to_csv('rfm_analysis.csv', index=False)
print("✅ RFM аналіз збережено у rfm_analysis.csv")

customer_analysis.to_csv('customer_analysis.csv', index=False)
print("✅ Аналіз клієнтів збережено у customer_analysis.csv")

# %% [markdown]
# ## 10. Підсумок

# %%
print("\n" + "="*70)
print("📊 ПІДСУМОК АНАЛІЗУ")
print("="*70)
print(f"\n👥 Клієнти:")
print(f"  Всього: {len(customers_df)}")
print(f"  VIP клієнтів: {len(rfm_df[rfm_df['segment'] == 'VIP'])}")
print(f"  Міст: {customers_df['city'].nunique()}")

print(f"\n📦 Замовлення:")
print(f"  Всього: {len(orders_df)}")
print(f"  Загальна сума: {orders_df['total_amount'].sum():.2f} грн")
print(f"  Середній чек: {orders_df['total_amount'].mean():.2f} грн")

print(f"\n🏆 Топ-3 клієнти:")
for idx, row in top_customers.head(3).iterrows():
    print(f"  {idx+1}. {row['customer_name']}: {row['total_spent']:.2f} грн")

print("\n✅ Аналіз завершено!")

# %%
# Закрити підключення
conn.close()
print("🔒 Підключення до БД закрито")
