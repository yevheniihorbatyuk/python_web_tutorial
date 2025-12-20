-- ============================================
-- Модуль 6.4: SQL Приклади та Задачі
-- ============================================
-- Цей файл містить різні SQL запити від простих до складних
-- З практичними задачами в стилі DataLemur

-- ============================================
-- РОЗДІЛ 1: ОСНОВИ SELECT
-- ============================================

-- 1.1 Прості запити
SELECT * FROM customers LIMIT 5;

SELECT first_name, last_name, email FROM customers;

SELECT * FROM products WHERE price > 10000;

SELECT * FROM products WHERE is_available = TRUE ORDER BY price DESC;

-- 1.2 WHERE з різними умовами
SELECT * FROM customers WHERE city = 'Kyiv';

SELECT * FROM products WHERE price BETWEEN 5000 AND 15000;

SELECT * FROM customers WHERE city IN ('Kyiv', 'Lviv', 'Kharkiv');

SELECT * FROM products WHERE name LIKE '%Phone%';

SELECT * FROM orders WHERE order_date >= '2024-10-01';

-- 1.3 Сортування та обмеження
SELECT * FROM products ORDER BY price DESC LIMIT 10;

SELECT * FROM customers ORDER BY registration_date DESC;

SELECT * FROM orders ORDER BY total_amount DESC LIMIT 5;


-- ============================================
-- РОЗДІЛ 2: АГРЕГАТНІ ФУНКЦІЇ
-- ============================================

-- 2.1 Базові агрегації
SELECT COUNT(*) AS total_customers FROM customers;

SELECT COUNT(*) AS total_products, AVG(price) AS avg_price FROM products;

SELECT MIN(price) AS min_price, MAX(price) AS max_price FROM products;

SELECT SUM(total_amount) AS total_revenue FROM orders;

-- 2.2 GROUP BY
SELECT city, COUNT(*) AS customer_count
FROM customers
GROUP BY city
ORDER BY customer_count DESC;

SELECT category_id, COUNT(*) AS product_count, AVG(price) AS avg_price
FROM products
GROUP BY category_id;

SELECT status, COUNT(*) AS order_count, SUM(total_amount) AS total_amount
FROM orders
GROUP BY status;

-- 2.3 HAVING (фільтрація після GROUP BY)
SELECT city, COUNT(*) AS customer_count
FROM customers
GROUP BY city
HAVING COUNT(*) >= 2
ORDER BY customer_count DESC;

SELECT category_id, AVG(price) AS avg_price
FROM products
GROUP BY category_id
HAVING AVG(price) > 10000;


-- ============================================
-- РОЗДІЛ 3: JOIN ЗАПИТИ
-- ============================================

-- 3.1 INNER JOIN - тільки співпадаючі рядки
SELECT
    o.id,
    c.first_name || ' ' || c.last_name AS customer_name,
    o.order_date,
    o.total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
ORDER BY o.order_date DESC;

-- 3.2 LEFT JOIN - всі з лівої таблиці + співпадаючі справа
SELECT
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(o.id) AS order_count,
    COALESCE(SUM(o.total_amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY total_spent DESC;

-- 3.3 Множинні JOIN
SELECT
    p.name AS product_name,
    c.name AS category_name,
    p.price,
    p.stock_quantity
FROM products p
INNER JOIN categories c ON p.category_id = c.id
ORDER BY c.name, p.price DESC;

-- 3.4 Складний JOIN з агрегацією
SELECT
    c.name AS category,
    COUNT(p.id) AS total_products,
    AVG(p.price) AS avg_price,
    SUM(p.stock_quantity) AS total_stock
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
GROUP BY c.id, c.name
ORDER BY total_products DESC;

-- 3.5 JOIN з кількома таблицями
SELECT
    o.id AS order_id,
    c.first_name || ' ' || c.last_name AS customer,
    e.first_name || ' ' || e.last_name AS employee,
    o.order_date,
    o.status,
    o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id
LEFT JOIN employees e ON o.employee_id = e.id
ORDER BY o.order_date DESC;


-- ============================================
-- РОЗДІЛ 4: SUBQUERY (Підзапити)
-- ============================================

-- 4.1 Subquery в WHERE
-- Товари дорожчі за середню ціну
SELECT name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;

-- 4.2 Subquery в SELECT
SELECT
    name,
    price,
    (SELECT AVG(price) FROM products) AS avg_price,
    price - (SELECT AVG(price) FROM products) AS price_diff
FROM products
ORDER BY price DESC;

-- 4.3 Subquery в FROM
SELECT
    category,
    avg_price,
    product_count
FROM (
    SELECT
        c.name AS category,
        AVG(p.price) AS avg_price,
        COUNT(p.id) AS product_count
    FROM categories c
    LEFT JOIN products p ON c.id = p.category_id
    GROUP BY c.id, c.name
) AS category_stats
WHERE product_count > 0
ORDER BY avg_price DESC;

-- 4.4 Subquery з EXISTS
-- Клієнти, які зробили хоча б одне замовлення
SELECT c.first_name, c.last_name, c.email
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- 4.5 Subquery з IN
-- Продукти, які були куплені
SELECT name, price
FROM products
WHERE id IN (
    SELECT DISTINCT product_id FROM order_items
)
ORDER BY price DESC;


-- ============================================
-- РОЗДІЛ 5: WINDOW FUNCTIONS
-- ============================================

-- 5.1 ROW_NUMBER - нумерація рядків
SELECT
    name,
    price,
    ROW_NUMBER() OVER (ORDER BY price DESC) AS price_rank
FROM products;

-- 5.2 RANK vs DENSE_RANK
SELECT
    name,
    price,
    RANK() OVER (ORDER BY price DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY price DESC) AS dense_rank
FROM products;

-- 5.3 PARTITION BY - нумерація в межах групи
SELECT
    c.name AS category,
    p.name AS product,
    p.price,
    ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY p.price DESC) AS rank_in_category
FROM products p
JOIN categories c ON p.category_id = c.id
ORDER BY c.name, rank_in_category;

-- 5.4 LAG та LEAD - доступ до попереднього/наступного рядка
SELECT
    order_date::DATE,
    total_amount,
    LAG(total_amount) OVER (ORDER BY order_date) AS prev_order_amount,
    LEAD(total_amount) OVER (ORDER BY order_date) AS next_order_amount
FROM orders
ORDER BY order_date;

-- 5.5 Аналіз продажів з накопиченням
SELECT
    order_date::DATE,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date) AS running_total,
    AVG(total_amount) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3
FROM orders
ORDER BY order_date;


-- ============================================
-- РОЗДІЛ 6: ЗАДАЧІ В СТИЛІ DATALEMUR
-- ============================================

-- ЗАДАЧА 1: Top 3 Products by Revenue
-- Знайти топ-3 продукти за виручкою
WITH product_revenue AS (
    SELECT
        p.id,
        p.name,
        SUM(oi.subtotal) AS total_revenue
    FROM products p
    JOIN order_items oi ON p.id = oi.product_id
    GROUP BY p.id, p.name
)
SELECT
    name,
    total_revenue
FROM product_revenue
ORDER BY total_revenue DESC
LIMIT 3;


-- ЗАДАЧА 2: Customer Lifetime Value
-- Розрахувати загальну вартість покупок для кожного клієнта
SELECT
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    COUNT(o.id) AS order_count,
    SUM(o.total_amount) AS lifetime_value,
    AVG(o.total_amount) AS avg_order_value
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name, c.email
HAVING COUNT(o.id) > 0
ORDER BY lifetime_value DESC;


-- ЗАДАЧА 3: Products Never Ordered
-- Знайти товари, які ніколи не купували
SELECT
    p.id,
    p.name,
    p.price,
    p.stock_quantity
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
WHERE oi.id IS NULL
ORDER BY p.price DESC;


-- ЗАДАЧА 4: Month-over-Month Growth
-- Розрахувати зростання продажів місяць до місяця
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS revenue
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    revenue - LAG(revenue) OVER (ORDER BY month) AS revenue_diff,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) /
        NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100,
        2
    ) AS growth_percentage
FROM monthly_revenue
ORDER BY month;


-- ЗАДАЧА 5: Top Selling Category per City
-- Найпопулярніша категорія товарів в кожному місті
WITH city_category_sales AS (
    SELECT
        c.city,
        cat.name AS category,
        SUM(oi.subtotal) AS total_sales,
        ROW_NUMBER() OVER (PARTITION BY c.city ORDER BY SUM(oi.subtotal) DESC) AS rank
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    JOIN categories cat ON p.category_id = cat.id
    GROUP BY c.city, cat.name
)
SELECT
    city,
    category,
    total_sales
FROM city_category_sales
WHERE rank = 1
ORDER BY total_sales DESC;


-- ЗАДАЧА 6: Employee Performance
-- Продуктивність співробітників (хто обробив найбільше замовлень)
SELECT
    e.first_name || ' ' || e.last_name AS employee_name,
    d.name AS department,
    COUNT(o.id) AS orders_processed,
    SUM(o.total_amount) AS total_revenue,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM employees e
JOIN departments d ON e.department_id = d.id
LEFT JOIN orders o ON e.id = o.employee_id
WHERE e.is_active = TRUE
GROUP BY e.id, e.first_name, e.last_name, d.name
HAVING COUNT(o.id) > 0
ORDER BY total_revenue DESC;


-- ЗАДАЧА 7: Product Pairs (Market Basket Analysis)
-- Які товари часто купують разом
SELECT
    p1.name AS product_1,
    p2.name AS product_2,
    COUNT(*) AS times_bought_together
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.id
JOIN products p2 ON oi2.product_id = p2.id
GROUP BY p1.name, p2.name
ORDER BY times_bought_together DESC
LIMIT 10;


-- ЗАДАЧА 8: Customers Who Haven't Ordered Recently
-- Клієнти, які не робили замовлень останні 30 днів
SELECT
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    MAX(o.order_date) AS last_order_date,
    CURRENT_DATE - MAX(o.order_date)::DATE AS days_since_last_order
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name, c.email
HAVING MAX(o.order_date) < CURRENT_DATE - INTERVAL '30 days'
ORDER BY days_since_last_order DESC;


-- ============================================
-- РОЗДІЛ 7: ОПТИМІЗАЦІЯ ТА ІНДЕКСИ
-- ============================================

-- Показати план виконання запиту
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 1;

-- Статистика використання індексів
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Розмір таблиць
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;


-- ============================================
-- РОЗДІЛ 8: КОРИСНІ АНАЛІТИЧНІ ЗАПИТИ
-- ============================================

-- 8.1 RFM Analysis (Recency, Frequency, Monetary)
WITH customer_rfm AS (
    SELECT
        c.id,
        c.first_name || ' ' || c.last_name AS customer_name,
        MAX(o.order_date) AS last_order_date,
        COUNT(o.id) AS order_count,
        SUM(o.total_amount) AS total_spent,
        CURRENT_DATE - MAX(o.order_date)::DATE AS recency_days
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    WHERE o.id IS NOT NULL
    GROUP BY c.id, c.first_name, c.last_name
)
SELECT
    customer_name,
    recency_days,
    order_count,
    total_spent,
    CASE
        WHEN recency_days <= 30 AND order_count >= 3 AND total_spent >= 50000 THEN 'VIP'
        WHEN recency_days <= 60 AND order_count >= 2 THEN 'Active'
        WHEN recency_days <= 90 THEN 'At Risk'
        ELSE 'Churned'
    END AS customer_segment
FROM customer_rfm
ORDER BY total_spent DESC;


-- 8.2 Cohort Analysis - Реєстрація по місяцях
SELECT
    DATE_TRUNC('month', registration_date) AS cohort_month,
    COUNT(*) AS new_customers
FROM customers
GROUP BY DATE_TRUNC('month', registration_date)
ORDER BY cohort_month;


-- 8.3 Inventory Value
SELECT
    c.name AS category,
    COUNT(p.id) AS products_count,
    SUM(p.stock_quantity) AS total_stock,
    SUM(p.price * p.stock_quantity) AS inventory_value
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
WHERE p.is_available = TRUE
GROUP BY c.id, c.name
ORDER BY inventory_value DESC;


-- ============================================
-- КІНЕЦЬ ПРИКЛАДІВ
-- ============================================
-- Для практики спробуйте:
-- 1. Модифікувати ці запити для інших даних
-- 2. Комбінувати різні техніки (JOIN + Window Functions)
-- 3. Створити власні аналітичні запити
-- 4. Оптимізувати повільні запити за допомогою EXPLAIN
-- ============================================
