-- ============================================
-- Advanced SQL for Data Science & Analytics
-- ============================================
-- Цей файл містить advanced SQL patterns для DS/DE:
-- - Window Functions для time-series
-- - Cohort Analysis
-- - Funnel Analysis
-- - Retention Analysis
-- - Statistical Functions
-- - Time-series Analysis

-- ============================================
-- 1. TIME-SERIES ANALYSIS
-- ============================================

-- 1.1 Moving Averages (для згладжування тренду)
SELECT
    order_date::DATE as date,
    SUM(total_amount) as daily_revenue,

    -- 7-day moving average
    AVG(SUM(total_amount)) OVER (
        ORDER BY order_date::DATE
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as ma_7day,

    -- 30-day moving average
    AVG(SUM(total_amount)) OVER (
        ORDER BY order_date::DATE
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as ma_30day
FROM orders
GROUP BY order_date::DATE
ORDER BY date;


-- 1.2 Running Totals та Cumulative Metrics
SELECT
    order_date::DATE as date,
    SUM(total_amount) as daily_revenue,

    -- Cumulative revenue
    SUM(SUM(total_amount)) OVER (
        ORDER BY order_date::DATE
    ) as cumulative_revenue,

    -- Running average
    AVG(SUM(total_amount)) OVER (
        ORDER BY order_date::DATE
    ) as running_avg_revenue
FROM orders
GROUP BY order_date::DATE
ORDER BY date;


-- 1.3 Year-over-Year Growth
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) as month,
        EXTRACT(YEAR FROM order_date) as year,
        EXTRACT(MONTH FROM order_date) as month_num,
        SUM(total_amount) as revenue
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date),
             EXTRACT(YEAR FROM order_date),
             EXTRACT(MONTH FROM order_date)
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (PARTITION BY month_num ORDER BY year) as prev_year_revenue,
    revenue - LAG(revenue) OVER (PARTITION BY month_num ORDER BY year) as yoy_growth,
    ROUND(
        (revenue - LAG(revenue) OVER (PARTITION BY month_num ORDER BY year)) /
        NULLIF(LAG(revenue) OVER (PARTITION BY month_num ORDER BY year), 0) * 100,
        2
    ) as yoy_growth_pct
FROM monthly_revenue
ORDER BY month;


-- ============================================
-- 2. COHORT ANALYSIS
-- ============================================

-- 2.1 Cohort Definition - групування по місяцю реєстрації
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', registration_date) as cohort_month
    FROM customers
),
-- 2.2 Order activity по місяцях
order_activity AS (
    SELECT
        c.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', o.order_date) as order_month,
        COUNT(o.id) as orders_count,
        SUM(o.total_amount) as total_spent
    FROM cohorts c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.id IS NOT NULL
    GROUP BY c.customer_id, c.cohort_month, DATE_TRUNC('month', o.order_date)
),
-- 2.3 Months since registration
cohort_periods AS (
    SELECT
        cohort_month,
        order_month,
        customer_id,
        orders_count,
        total_spent,
        EXTRACT(MONTH FROM AGE(order_month, cohort_month)) as months_since_cohort
    FROM order_activity
)
-- 2.4 Cohort metrics
SELECT
    cohort_month,
    months_since_cohort,
    COUNT(DISTINCT customer_id) as active_customers,
    SUM(orders_count) as total_orders,
    SUM(total_spent) as total_revenue,
    AVG(total_spent) as avg_revenue_per_customer
FROM cohort_periods
GROUP BY cohort_month, months_since_cohort
ORDER BY cohort_month, months_since_cohort;


-- 2.5 Retention Rate по Cohorts
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', registration_date) as cohort_month
    FROM customers
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(*) as cohort_size
    FROM cohorts
    GROUP BY cohort_month
),
monthly_activity AS (
    SELECT
        c.cohort_month,
        DATE_TRUNC('month', o.order_date) as activity_month,
        EXTRACT(MONTH FROM AGE(o.order_date, c.cohort_month)) as months_since_cohort,
        COUNT(DISTINCT c.customer_id) as active_customers
    FROM cohorts c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.cohort_month, DATE_TRUNC('month', o.order_date),
             EXTRACT(MONTH FROM AGE(o.order_date, c.cohort_month))
)
SELECT
    ma.cohort_month,
    ma.months_since_cohort,
    ma.active_customers,
    cs.cohort_size,
    ROUND(ma.active_customers::NUMERIC / cs.cohort_size * 100, 2) as retention_rate
FROM monthly_activity ma
JOIN cohort_sizes cs ON ma.cohort_month = cs.cohort_month
ORDER BY ma.cohort_month, ma.months_since_cohort;


-- ============================================
-- 3. FUNNEL ANALYSIS
-- ============================================

-- E-commerce funnel: Registration → First Order → Repeat Order
WITH funnel_steps AS (
    SELECT
        c.id as customer_id,
        c.registration_date as step1_registration,
        MIN(o.order_date) as step2_first_order,
        CASE WHEN COUNT(o.id) > 1
             THEN MAX(o.order_date)
             ELSE NULL
        END as step3_repeat_order
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.registration_date
)
SELECT
    'Step 1: Registered' as funnel_step,
    COUNT(*) as users,
    100.0 as conversion_rate
FROM funnel_steps

UNION ALL

SELECT
    'Step 2: First Order' as funnel_step,
    COUNT(*) as users,
    ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM funnel_steps) * 100, 2) as conversion_rate
FROM funnel_steps
WHERE step2_first_order IS NOT NULL

UNION ALL

SELECT
    'Step 3: Repeat Order' as funnel_step,
    COUNT(*) as users,
    ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM funnel_steps) * 100, 2) as conversion_rate
FROM funnel_steps
WHERE step3_repeat_order IS NOT NULL;


-- ============================================
-- 4. CUSTOMER SEGMENTATION (RFM Advanced)
-- ============================================

WITH rfm_calc AS (
    SELECT
        c.id as customer_id,
        c.first_name || ' ' || c.last_name as customer_name,

        -- Recency (днів з останнього замовлення)
        COALESCE(CURRENT_DATE - MAX(o.order_date)::DATE, 999) as recency,

        -- Frequency (кількість замовлень)
        COUNT(o.id) as frequency,

        -- Monetary (загальна сума)
        COALESCE(SUM(o.total_amount), 0) as monetary
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.first_name, c.last_name
),
rfm_scores AS (
    SELECT
        *,
        -- RFM scores (1-5, where 5 is best)
        NTILE(5) OVER (ORDER BY recency ASC) as r_score,  -- Менше днів = краще
        NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) as m_score
    FROM rfm_calc
),
rfm_segments AS (
    SELECT
        *,
        (r_score + f_score + m_score) as rfm_total,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Potential Loyalist'
        END as segment
    FROM rfm_scores
)
SELECT
    segment,
    COUNT(*) as customer_count,
    ROUND(AVG(recency), 1) as avg_recency,
    ROUND(AVG(frequency), 1) as avg_frequency,
    ROUND(AVG(monetary), 2) as avg_monetary,
    ROUND(SUM(monetary), 2) as total_revenue
FROM rfm_segments
GROUP BY segment
ORDER BY total_revenue DESC;


-- ============================================
-- 5. PRODUCT AFFINITY ANALYSIS (Market Basket)
-- ============================================

-- Які товари часто купують разом?
WITH product_pairs AS (
    SELECT
        oi1.product_id as product_a_id,
        oi2.product_id as product_b_id,
        COUNT(DISTINCT oi1.order_id) as times_together
    FROM order_items oi1
    JOIN order_items oi2
        ON oi1.order_id = oi2.order_id
        AND oi1.product_id < oi2.product_id
    GROUP BY oi1.product_id, oi2.product_id
    HAVING COUNT(DISTINCT oi1.order_id) >= 2
)
SELECT
    p1.name as product_a,
    p2.name as product_b,
    pp.times_together,
    -- Lift (наскільки частіше купують разом vs окремо)
    ROUND(
        pp.times_together::NUMERIC /
        ((SELECT COUNT(DISTINCT order_id) FROM order_items WHERE product_id = pp.product_a_id) *
         (SELECT COUNT(DISTINCT order_id) FROM order_items WHERE product_id = pp.product_b_id)::NUMERIC /
         (SELECT COUNT(DISTINCT id) FROM orders)::NUMERIC),
        2
    ) as lift
FROM product_pairs pp
JOIN products p1 ON pp.product_a_id = p1.id
JOIN products p2 ON pp.product_b_id = p2.id
ORDER BY pp.times_together DESC, lift DESC
LIMIT 10;


-- ============================================
-- 6. ABC ANALYSIS (Pareto 80/20)
-- ============================================

-- Класифікація товарів за виручкою (A, B, C)
WITH product_revenue AS (
    SELECT
        p.id,
        p.name,
        COALESCE(SUM(oi.subtotal), 0) as total_revenue
    FROM products p
    LEFT JOIN order_items oi ON p.id = oi.product_id
    GROUP BY p.id, p.name
),
ranked_products AS (
    SELECT
        *,
        SUM(total_revenue) OVER () as total_market_revenue,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC) as cumulative_revenue
    FROM product_revenue
),
classified_products AS (
    SELECT
        *,
        cumulative_revenue / total_market_revenue * 100 as cumulative_percentage,
        CASE
            WHEN cumulative_revenue / total_market_revenue <= 0.8 THEN 'A'
            WHEN cumulative_revenue / total_market_revenue <= 0.95 THEN 'B'
            ELSE 'C'
        END as abc_class
    FROM ranked_products
)
SELECT
    abc_class,
    COUNT(*) as product_count,
    ROUND(SUM(total_revenue), 2) as class_revenue,
    ROUND(SUM(total_revenue) / MAX(total_market_revenue) * 100, 2) as revenue_percentage
FROM classified_products
GROUP BY abc_class
ORDER BY abc_class;


-- ============================================
-- 7. STATISTICAL FUNCTIONS
-- ============================================

-- 7.1 Percentiles та Distribution
SELECT
    'Order Value Distribution' as metric,
    ROUND(MIN(total_amount), 2) as min,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_amount), 2) as p25,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY total_amount), 2) as median,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_amount), 2) as p75,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_amount), 2) as p95,
    ROUND(MAX(total_amount), 2) as max,
    ROUND(AVG(total_amount), 2) as mean,
    ROUND(STDDEV(total_amount), 2) as std_dev
FROM orders;


-- 7.2 Outlier Detection (IQR method)
WITH stats AS (
    SELECT
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_amount) as q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_amount) as q3
    FROM orders
),
bounds AS (
    SELECT
        q1 - 1.5 * (q3 - q1) as lower_bound,
        q3 + 1.5 * (q3 - q1) as upper_bound
    FROM stats
)
SELECT
    o.id,
    o.customer_id,
    o.total_amount,
    CASE
        WHEN o.total_amount < b.lower_bound THEN 'Lower Outlier'
        WHEN o.total_amount > b.upper_bound THEN 'Upper Outlier'
        ELSE 'Normal'
    END as outlier_status
FROM orders o
CROSS JOIN bounds b
WHERE o.total_amount < b.lower_bound OR o.total_amount > b.upper_bound
ORDER BY o.total_amount DESC;


-- 7.3 Correlation (Spearman rank correlation approximation)
-- Корелація між ціною товару та кількістю продажів
WITH product_metrics AS (
    SELECT
        p.id,
        p.price,
        COUNT(oi.id) as sales_count,
        ROW_NUMBER() OVER (ORDER BY p.price) as price_rank,
        ROW_NUMBER() OVER (ORDER BY COUNT(oi.id)) as sales_rank
    FROM products p
    LEFT JOIN order_items oi ON p.id = oi.product_id
    GROUP BY p.id, p.price
)
SELECT
    COUNT(*) as n,
    ROUND(
        1 - (6 * SUM(POWER(price_rank - sales_rank, 2))) /
        (COUNT(*) * (POWER(COUNT(*), 2) - 1)),
        3
    ) as spearman_correlation
FROM product_metrics;


-- ============================================
-- 8. TIME-SERIES FORECASTING FEATURES
-- ============================================

-- Створення features для ML time-series forecasting
WITH daily_sales AS (
    SELECT
        order_date::DATE as date,
        SUM(total_amount) as revenue,
        COUNT(*) as order_count
    FROM orders
    GROUP BY order_date::DATE
),
lagged_features AS (
    SELECT
        date,
        revenue,
        order_count,

        -- Lag features (previous days)
        LAG(revenue, 1) OVER (ORDER BY date) as revenue_lag_1,
        LAG(revenue, 7) OVER (ORDER BY date) as revenue_lag_7,
        LAG(revenue, 30) OVER (ORDER BY date) as revenue_lag_30,

        -- Rolling features
        AVG(revenue) OVER (
            ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as revenue_ma_7,

        STDDEV(revenue) OVER (
            ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as revenue_std_7,

        -- Date features
        EXTRACT(DOW FROM date) as day_of_week,
        EXTRACT(DAY FROM date) as day_of_month,
        EXTRACT(MONTH FROM date) as month,
        EXTRACT(QUARTER FROM date) as quarter,

        -- Is weekend
        CASE WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN 1 ELSE 0 END as is_weekend
    FROM daily_sales
)
SELECT * FROM lagged_features
WHERE revenue_lag_30 IS NOT NULL  -- Remove initial rows with NULLs
ORDER BY date;


-- ============================================
-- 9. CHURN PREDICTION FEATURES
-- ============================================

-- Features для ML churn prediction model
WITH customer_orders AS (
    SELECT
        c.id as customer_id,
        c.registration_date,
        COUNT(o.id) as total_orders,
        COALESCE(SUM(o.total_amount), 0) as total_spent,
        COALESCE(AVG(o.total_amount), 0) as avg_order_value,
        MIN(o.order_date) as first_order_date,
        MAX(o.order_date) as last_order_date,
        STDDEV(o.total_amount) as order_value_std
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.registration_date
),
time_features AS (
    SELECT
        *,
        CURRENT_DATE - registration_date::DATE as customer_age_days,
        CURRENT_DATE - last_order_date::DATE as days_since_last_order,
        CASE WHEN total_orders > 0
             THEN (last_order_date::DATE - first_order_date::DATE)::NUMERIC / NULLIF(total_orders - 1, 0)
             ELSE NULL
        END as avg_days_between_orders
    FROM customer_orders
)
SELECT
    customer_id,
    total_orders,
    total_spent,
    avg_order_value,
    COALESCE(order_value_std, 0) as order_value_std,
    customer_age_days,
    COALESCE(days_since_last_order, 999) as days_since_last_order,
    COALESCE(avg_days_between_orders, 0) as avg_days_between_orders,

    -- Derived features
    CASE WHEN total_orders > 0
         THEN total_spent / customer_age_days * 30
         ELSE 0
    END as monthly_spending_rate,

    -- Target variable (churn label)
    CASE WHEN days_since_last_order > 90 THEN 1 ELSE 0 END as is_churned
FROM time_features;


-- ============================================
-- КІНЕЦЬ ADVANCED SQL
-- ============================================
-- Ці запити демонструють:
-- 1. Time-series analysis та forecasting features
-- 2. Cohort analysis для retention
-- 3. Funnel analysis для conversion
-- 4. Statistical functions
-- 5. Product affinity (market basket)
-- 6. ML feature engineering
-- 7. Churn prediction features
--
-- В production:
-- - Ці запити стають Airflow/dbt jobs
-- - Features зберігаються в Feature Store
-- - Використовуються для ML models
-- ============================================
