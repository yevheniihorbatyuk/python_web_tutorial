"""
Feature Store для ML Pipeline
==============================

Modern ML інфраструктура паттерн:
- Централізоване сховище features для ML models
- Offline features (training) + Online features (serving)
- Feature versioning та lineage
- Real-time feature computation

Use Cases:
- ML model training з consistent features
- Real-time predictions з low latency
- Feature reusability між models
- A/B testing нових features

Tech Stack (спрощена версія):
- PostgreSQL для offline features
- Redis для online features (швидкий lookup)
- Pandas для feature engineering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from colorama import Fore, init
import json

init(autoreset=True)


# ============================================
# FEATURE DEFINITIONS
# ============================================

@dataclass
class FeatureDefinition:
    """Metadata про feature"""
    name: str
    description: str
    feature_type: str  # "numerical", "categorical", "boolean"
    entity: str  # "customer", "product", etc.
    version: str = "v1"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'feature_type': self.feature_type,
            'entity': self.entity,
            'version': self.version,
            'created_at': self.created_at.isoformat()
        }


# ============================================
# FEATURE STORE
# ============================================

class FeatureStore:
    """
    Feature Store для ML pipeline

    Pattern:
    1. Offline Store (PostgreSQL) - для training
    2. Online Store (Redis/memory) - для serving
    3. Feature Registry - metadata про features
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._init_tables()

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string)

    def _init_tables(self):
        """Initialize feature store tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Feature Registry - metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_registry (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                feature_type VARCHAR(50),
                entity VARCHAR(50),
                version VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Customer Features - offline store
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_features (
                customer_id INTEGER PRIMARY KEY,

                -- RFM Features
                recency_days INTEGER,
                frequency INTEGER,
                monetary_value DECIMAL(12,2),

                -- Behavioral Features
                avg_order_value DECIMAL(10,2),
                days_since_registration INTEGER,
                total_orders INTEGER,

                -- Derived Features
                customer_lifetime_value DECIMAL(12,2),
                churn_risk_score DECIMAL(3,2),
                customer_segment VARCHAR(50),

                -- Metadata
                computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version VARCHAR(20) DEFAULT 'v1'
            );
        """)

        # Product Features
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_features (
                product_id INTEGER PRIMARY KEY,

                -- Popularity Features
                total_orders INTEGER,
                total_quantity_sold INTEGER,
                total_revenue DECIMAL(12,2),

                -- Time Features
                days_since_last_order INTEGER,
                avg_orders_per_week DECIMAL(6,2),

                -- Price Features
                current_price DECIMAL(10,2),
                avg_selling_price DECIMAL(10,2),
                price_percentile DECIMAL(3,2),

                computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version VARCHAR(20) DEFAULT 'v1'
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()

    # ============================================
    # FEATURE ENGINEERING
    # ============================================

    def compute_customer_features(self) -> pd.DataFrame:
        """
        Compute customer features з raw data
        Production: це буде Spark/Dask job
        """
        print(f"{Fore.YELLOW}🔧 Computing customer features...")

        conn = self._get_connection()

        # Complex SQL для feature extraction
        query = """
        WITH customer_orders AS (
            SELECT
                c.id as customer_id,
                c.first_name,
                c.last_name,
                c.city,
                c.registration_date,
                COUNT(o.id) as total_orders,
                COALESCE(SUM(o.total_amount), 0) as total_spent,
                COALESCE(AVG(o.total_amount), 0) as avg_order_value,
                MAX(o.order_date) as last_order_date,
                CURRENT_DATE - c.registration_date::DATE as days_since_registration,
                CURRENT_DATE - MAX(o.order_date)::DATE as recency_days
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id, c.first_name, c.last_name, c.city, c.registration_date
        ),
        customer_metrics AS (
            SELECT
                *,
                -- Customer Lifetime Value (простий розрахунок)
                total_spent * 1.5 as customer_lifetime_value,

                -- Churn Risk Score (0-1)
                CASE
                    WHEN recency_days > 90 THEN 0.8
                    WHEN recency_days > 60 THEN 0.5
                    WHEN recency_days > 30 THEN 0.2
                    ELSE 0.1
                END as churn_risk_score,

                -- Customer Segment
                CASE
                    WHEN total_orders >= 3 AND total_spent > 50000 THEN 'VIP'
                    WHEN total_orders >= 2 AND total_spent > 20000 THEN 'Loyal'
                    WHEN total_orders >= 1 THEN 'Active'
                    ELSE 'New'
                END as customer_segment
            FROM customer_orders
        )
        SELECT * FROM customer_metrics;
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        print(f"{Fore.GREEN}✓ Computed {len(df)} customer feature sets")
        return df

    def compute_product_features(self) -> pd.DataFrame:
        """Compute product features"""
        print(f"{Fore.YELLOW}🔧 Computing product features...")

        conn = self._get_connection()

        query = """
        WITH product_metrics AS (
            SELECT
                p.id as product_id,
                p.name,
                p.price as current_price,
                COUNT(oi.id) as total_orders,
                COALESCE(SUM(oi.quantity), 0) as total_quantity_sold,
                COALESCE(SUM(oi.subtotal), 0) as total_revenue,
                COALESCE(AVG(oi.price_at_purchase), 0) as avg_selling_price,
                MAX(o.order_date) as last_order_date,
                CURRENT_DATE - MAX(o.order_date)::DATE as days_since_last_order
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            GROUP BY p.id, p.name, p.price
        ),
        price_percentiles AS (
            SELECT
                product_id,
                PERCENT_RANK() OVER (ORDER BY current_price) as price_percentile
            FROM product_metrics
        )
        SELECT
            pm.*,
            pp.price_percentile,
            -- Orders per week
            CASE
                WHEN days_since_last_order > 0
                THEN total_orders::DECIMAL / (days_since_last_order / 7.0)
                ELSE 0
            END as avg_orders_per_week
        FROM product_metrics pm
        JOIN price_percentiles pp ON pm.product_id = pp.product_id;
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        print(f"{Fore.GREEN}✓ Computed {len(df)} product feature sets")
        return df

    # ============================================
    # FEATURE STORE OPERATIONS
    # ============================================

    def save_features(self, entity_type: str, features_df: pd.DataFrame):
        """
        Save features до offline store
        В production: це буде batch job (Airflow/Prefect)
        """
        print(f"{Fore.YELLOW}💾 Saving {entity_type} features to offline store...")

        conn = self._get_connection()
        cursor = conn.cursor()

        if entity_type == "customer":
            # Prepare data
            features_df['computed_at'] = datetime.now()
            features_df['version'] = 'v1'

            # Build upsert query
            columns = ['customer_id', 'recency_days', 'frequency', 'monetary_value',
                      'avg_order_value', 'days_since_registration', 'total_orders',
                      'customer_lifetime_value', 'churn_risk_score', 'customer_segment',
                      'computed_at', 'version']

            # Rename DataFrame columns to match DB
            df_renamed = features_df.rename(columns={
                'total_spent': 'monetary_value',
                'total_orders': 'frequency'
            })

            values = []
            for _, row in df_renamed.iterrows():
                values.append(tuple(row[col] for col in columns))

            # UPSERT query
            query = """
                INSERT INTO customer_features
                (customer_id, recency_days, frequency, monetary_value, avg_order_value,
                 days_since_registration, total_orders, customer_lifetime_value,
                 churn_risk_score, customer_segment, computed_at, version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) DO UPDATE SET
                    recency_days = EXCLUDED.recency_days,
                    frequency = EXCLUDED.frequency,
                    monetary_value = EXCLUDED.monetary_value,
                    avg_order_value = EXCLUDED.avg_order_value,
                    days_since_registration = EXCLUDED.days_since_registration,
                    total_orders = EXCLUDED.total_orders,
                    customer_lifetime_value = EXCLUDED.customer_lifetime_value,
                    churn_risk_score = EXCLUDED.churn_risk_score,
                    customer_segment = EXCLUDED.customer_segment,
                    computed_at = EXCLUDED.computed_at,
                    version = EXCLUDED.version;
            """

            execute_batch(cursor, query, values, page_size=100)

        elif entity_type == "product":
            # Similar for products
            features_df['computed_at'] = datetime.now()
            features_df['version'] = 'v1'

            columns = ['product_id', 'total_orders', 'total_quantity_sold', 'total_revenue',
                      'days_since_last_order', 'avg_orders_per_week', 'current_price',
                      'avg_selling_price', 'price_percentile', 'computed_at', 'version']

            values = []
            for _, row in features_df.iterrows():
                values.append(tuple(row[col] for col in columns))

            query = """
                INSERT INTO product_features
                (product_id, total_orders, total_quantity_sold, total_revenue,
                 days_since_last_order, avg_orders_per_week, current_price,
                 avg_selling_price, price_percentile, computed_at, version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    total_orders = EXCLUDED.total_orders,
                    total_quantity_sold = EXCLUDED.total_quantity_sold,
                    total_revenue = EXCLUDED.total_revenue,
                    days_since_last_order = EXCLUDED.days_since_last_order,
                    avg_orders_per_week = EXCLUDED.avg_orders_per_week,
                    current_price = EXCLUDED.current_price,
                    avg_selling_price = EXCLUDED.avg_selling_price,
                    price_percentile = EXCLUDED.price_percentile,
                    computed_at = EXCLUDED.computed_at,
                    version = EXCLUDED.version;
            """

            execute_batch(cursor, query, values, page_size=100)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"{Fore.GREEN}✓ Saved {len(features_df)} {entity_type} feature sets")

    def get_features(self, entity_type: str, entity_ids: List[int]) -> pd.DataFrame:
        """
        Get features для specific entities
        Online serving pattern
        """
        conn = self._get_connection()

        if entity_type == "customer":
            placeholders = ','.join(['%s'] * len(entity_ids))
            query = f"SELECT * FROM customer_features WHERE customer_id IN ({placeholders})"
        elif entity_type == "product":
            placeholders = ','.join(['%s'] * len(entity_ids))
            query = f"SELECT * FROM product_features WHERE product_id IN ({placeholders})"
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")

        df = pd.read_sql_query(query, conn, params=entity_ids)
        conn.close()

        return df

    def get_training_dataset(self, entity_type: str,
                            feature_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get features для ML training
        Point-in-time correct features
        """
        print(f"{Fore.YELLOW}📊 Preparing training dataset for {entity_type}...")

        conn = self._get_connection()

        if entity_type == "customer":
            if feature_names:
                columns = ['customer_id'] + feature_names
                column_str = ', '.join(columns)
            else:
                column_str = '*'

            query = f"SELECT {column_str} FROM customer_features"

        df = pd.read_sql_query(query, conn)
        conn.close()

        print(f"{Fore.GREEN}✓ Training dataset ready: {df.shape}")
        return df


# ============================================
# ML MODEL EXAMPLE
# ============================================

class ChurnPredictionModel:
    """
    Простий ML model який використовує Feature Store
    В production: sklearn, XGBoost, TensorFlow, etc.
    """

    def __init__(self, feature_store: FeatureStore):
        self.feature_store = feature_store
        self.model = None  # Тут буде trained model

    def prepare_features(self, customer_ids: List[int]) -> pd.DataFrame:
        """Get features для prediction"""
        features = self.feature_store.get_features("customer", customer_ids)

        # Select relevant features
        feature_columns = [
            'recency_days', 'frequency', 'monetary_value',
            'avg_order_value', 'days_since_registration'
        ]

        return features[['customer_id'] + feature_columns]

    def predict_churn(self, customer_ids: List[int]) -> Dict[int, float]:
        """
        Predict churn probability
        В production: використовуємо trained model
        Тут: простий rule-based для демонстрації
        """
        features_df = self.prepare_features(customer_ids)

        predictions = {}
        for _, row in features_df.iterrows():
            # Simple rule-based (в production: model.predict)
            if row['recency_days'] > 90:
                churn_prob = 0.8
            elif row['recency_days'] > 60:
                churn_prob = 0.5
            elif row['recency_days'] > 30:
                churn_prob = 0.2
            else:
                churn_prob = 0.1

            predictions[row['customer_id']] = churn_prob

        return predictions


# ============================================
# DEMO
# ============================================

def demo_feature_engineering():
    """Demo: compute features"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}1. Feature Engineering")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Initialize feature store
    connection_string = "host=localhost dbname=learning_db user=admin password=admin123"
    fs = FeatureStore(connection_string)

    # Compute customer features
    customer_features = fs.compute_customer_features()
    print(f"\n{Fore.CYAN}Sample Customer Features:")
    print(customer_features[['customer_id', 'first_name', 'total_orders',
                             'churn_risk_score', 'customer_segment']].head())

    # Compute product features
    product_features = fs.compute_product_features()
    print(f"\n{Fore.CYAN}Sample Product Features:")
    print(product_features[['product_id', 'name', 'total_revenue',
                            'price_percentile']].head())

    return fs, customer_features, product_features


def demo_feature_store_operations(fs, customer_features, product_features):
    """Demo: save and retrieve features"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}2. Feature Store Operations")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Save features
    fs.save_features("customer", customer_features)
    fs.save_features("product", product_features)

    # Retrieve features for specific customers
    print(f"\n{Fore.YELLOW}📖 Retrieving features for customers [1, 2, 3]...")
    features = fs.get_features("customer", [1, 2, 3])
    print(features[['customer_id', 'frequency', 'monetary_value', 'churn_risk_score']])


def demo_ml_inference(fs):
    """Demo: ML model inference з feature store"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}3. ML Model Inference")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Create model
    model = ChurnPredictionModel(fs)

    # Predict churn for customers
    customer_ids = [1, 2, 3, 4, 5]
    print(f"{Fore.YELLOW}🤖 Predicting churn for customers {customer_ids}...")
    predictions = model.predict_churn(customer_ids)

    print(f"\n{Fore.CYAN}Churn Predictions:")
    for customer_id, churn_prob in predictions.items():
        risk = "🔴 HIGH" if churn_prob > 0.6 else "🟡 MEDIUM" if churn_prob > 0.3 else "🟢 LOW"
        print(f"{Fore.WHITE}  Customer {customer_id}: {churn_prob:.1%} {risk}")


def main():
    """Main demo"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}  FEATURE STORE - ML Infrastructure Pattern")
    print(f"{Fore.CYAN}{'='*70}\n")

    # Run demos
    fs, customer_features, product_features = demo_feature_engineering()
    demo_feature_store_operations(fs, customer_features, product_features)
    demo_ml_inference(fs)

    # Summary
    print(f"\n{Fore.YELLOW}📚 Key Concepts:")
    print(f"{Fore.WHITE}  1. Feature Engineering - compute features з raw data")
    print(f"{Fore.WHITE}  2. Offline Store - features для training")
    print(f"{Fore.WHITE}  3. Online Store - features для serving")
    print(f"{Fore.WHITE}  4. Feature Versioning - track feature changes")
    print(f"{Fore.WHITE}  5. Point-in-time Correctness - no data leakage")

    print(f"\n{Fore.CYAN}💡 Production Tools:")
    print(f"{Fore.WHITE}  • Feast - Open-source feature store")
    print(f"{Fore.WHITE}  • Tecton - Managed feature platform")
    print(f"{Fore.WHITE}  • AWS SageMaker Feature Store")
    print(f"{Fore.WHITE}  • Databricks Feature Store")
    print(f"{Fore.WHITE}  • Google Vertex AI Feature Store\n")


if __name__ == "__main__":
    main()
