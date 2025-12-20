"""
Module 8.2: MongoDB - Advanced Patterns & Real-world Use Cases
==============================================================

MongoDB practical examples for Senior Data Engineers:
- Document structure design for Data Science applications
- Aggregation pipeline (like SQL GROUP BY, JOIN, etc.)
- Indexing strategies
- Change streams monitoring
- Bulk operations for high-volume data
- Time-series data handling

Author: Senior Data Science Engineer
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, BulkWriteError
from pymongo.operations import InsertOne, UpdateOne
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import logging
from pprint import pprint

# ============================================================================
# CONFIGURATION
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# For local MongoDB (you can use MongoDB Atlas connection string instead)
MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "data_science_db"

# For MongoDB Atlas (cloud):
# MONGODB_URL = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"


# ============================================================================
# DATA MODEL EXAMPLES
# ============================================================================

# Document structure for events/logs (Time-series data)
EVENT_EXAMPLE = {
    "_id": "auto_generated",
    "user_id": 12345,
    "event_type": "user_purchase",
    "timestamp": "2024-01-15T10:30:00Z",
    "metadata": {
        "product_id": "PROD-001",
        "price": 99.99,
        "currency": "USD",
        "category": "electronics"
    },
    "geo": {
        "country": "Ukraine",
        "city": "Kyiv",
        "coordinates": [50.4501, 30.5234]  # GeoJSON format
    },
    "session_info": {
        "device": "mobile",
        "os": "iOS",
        "app_version": "2.1.0"
    }
}

# Document structure for user profiles
USER_PROFILE_EXAMPLE = {
    "_id": "auto_generated",
    "username": "data_scientist_001",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z",
    "profile": {
        "interests": ["data-science", "machine-learning", "python"],
        "expertise_level": "senior",
        "total_projects": 25
    },
    "metrics": {
        "last_active": "2024-01-15T10:30:00Z",
        "total_views": 1500,
        "avg_engagement_score": 8.5
    },
    "subscriptions": [
        {
            "plan": "premium",
            "started": "2023-06-01T00:00:00Z",
            "expires": "2024-06-01T00:00:00Z",
            "auto_renew": True
        }
    ]
}


# ============================================================================
# MONGODB CONNECTION & COLLECTION MANAGEMENT
# ============================================================================

class MongoDBManager:
    """Manager for MongoDB operations."""

    def __init__(self, connection_string: str = MONGODB_URL, db_name: str = DATABASE_NAME):
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]

            # Verify connection
            self.client.server_info()
            logger.info(f"✓ Connected to MongoDB: {db_name}")
        except Exception as e:
            logger.error(f"✗ Failed to connect to MongoDB: {str(e)}")
            logger.info("Using mock database for demonstration...")
            self.client = None
            self.db = None

    def create_collections_with_schema(self) -> None:
        """Create collections with schema validation and indexing."""
        if not self.client:
            logger.warning("MongoDB not available - skipping collection creation")
            return

        collections_config = {
            "users": {
                "validation": {
                    "bsonType": "object",
                    "required": ["username", "email"],
                    "properties": {
                        "username": {"bsonType": "string"},
                        "email": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},
                        "profile": {"bsonType": "object"},
                        "metrics": {"bsonType": "object"}
                    }
                },
                "indexes": [
                    (("username",), {"unique": True}),
                    (("email",), {"unique": True}),
                    (("created_at", DESCENDING), {})
                ]
            },
            "events": {
                "validation": {
                    "bsonType": "object",
                    "required": ["user_id", "event_type", "timestamp"],
                    "properties": {
                        "user_id": {"bsonType": "int"},
                        "event_type": {"bsonType": "string"},
                        "timestamp": {"bsonType": "date"}
                    }
                },
                "indexes": [
                    (("user_id",), {}),
                    (("timestamp", DESCENDING), {}),
                    (("event_type",), {}),
                    (("geo.coordinates",), {"2dsphere"})  # Geospatial index
                ]
            },
            "analytics": {
                "validation": None,
                "indexes": [
                    (("date",), {}),
                    (("user_id",), {})
                ]
            }
        }

        for collection_name, config in collections_config.items():
            if collection_name not in self.db.list_collection_names():
                # Create collection with validation
                if config["validation"]:
                    self.db.create_collection(
                        collection_name,
                        validator={"$jsonSchema": config["validation"]}
                    )
                else:
                    self.db.create_collection(collection_name)

                logger.info(f"✓ Created collection: {collection_name}")

                # Create indexes
                collection = self.db[collection_name]
                for index_spec, index_options in config["indexes"]:
                    try:
                        collection.create_index(index_spec, **index_options)
                    except Exception as e:
                        logger.warning(f"Index creation failed: {str(e)}")

    def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# ============================================================================
# USER MANAGEMENT
# ============================================================================

class UserManager:
    """Manage user documents in MongoDB."""

    def __init__(self, db):
        self.collection = db.users if db else None

    def insert_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Insert a new user document."""
        if not self.collection:
            return None

        try:
            result = self.collection.insert_one(user_data)
            logger.info(f"✓ User inserted: {result.inserted_id}")
            return str(result.inserted_id)
        except DuplicateKeyError:
            logger.error(f"✗ User already exists: {user_data.get('email')}")
            return None

    def find_user_by_username(self, username: str) -> Optional[Dict]:
        """Find user by username."""
        if not self.collection:
            return None

        return self.collection.find_one({"username": username})

    def find_users_by_interest(self, interest: str) -> List[Dict]:
        """Find users interested in a specific topic."""
        if not self.collection:
            return []

        return list(self.collection.find({
            "profile.interests": interest
        }))

    def bulk_insert_users(self, users: List[Dict[str, Any]]) -> None:
        """Insert multiple users efficiently."""
        if not self.collection:
            return

        operations = [InsertOne(user) for user in users]

        try:
            result = self.collection.bulk_write(operations)
            logger.info(f"✓ Inserted {result.inserted_count} users")
        except BulkWriteError as e:
            logger.warning(f"⚠ Partial bulk write: {e.details}")

    def update_user_metrics(self, user_id: str, metrics_update: Dict) -> None:
        """Update user metrics."""
        if not self.collection:
            return

        self.collection.update_one(
            {"_id": user_id},
            {"$set": {"metrics": metrics_update}}
        )

    def add_subscription(self, user_id: str, subscription: Dict) -> None:
        """Add subscription to user."""
        if not self.collection:
            return

        self.collection.update_one(
            {"_id": user_id},
            {"$push": {"subscriptions": subscription}}
        )


# ============================================================================
# EVENT TRACKING & ANALYTICS
# ============================================================================

class EventTracker:
    """Track and analyze user events."""

    def __init__(self, db):
        self.collection = db.events if db else None

    def log_event(self, event_data: Dict[str, Any]) -> None:
        """Log a user event."""
        if not self.collection:
            return

        event_data['timestamp'] = datetime.utcnow()
        self.collection.insert_one(event_data)

    def get_user_events(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get recent events for a user."""
        if not self.collection:
            return []

        return list(self.collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit))

    def get_event_distribution(self) -> Dict[str, int]:
        """
        Get distribution of event types.
        Demonstrates: Simple aggregation.
        """
        if not self.collection:
            return {}

        pipeline = [
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]

        result = list(self.collection.aggregate(pipeline))
        return {item["_id"]: item["count"] for item in result}

    def get_user_activity_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Get aggregated user activity metrics.
        Demonstrates: Complex aggregation pipeline.
        """
        if not self.collection:
            return {}

        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$user_id",
                    "event_count": {"$sum": 1},
                    "event_types": {"$push": "$event_type"},
                    "last_event": {"$max": "$timestamp"}
                }
            },
            {
                "$sort": {"event_count": -1}
            },
            {
                "$limit": 10
            }
        ]

        return list(self.collection.aggregate(pipeline))

    def get_purchase_analytics(self) -> Dict:
        """
        Analyze purchase events.
        Demonstrates: Filtering and field extraction in aggregation.
        """
        if not self.collection:
            return {}

        pipeline = [
            {
                "$match": {"event_type": "user_purchase"}
            },
            {
                "$group": {
                    "_id": "$metadata.category",
                    "total_revenue": {"$sum": "$metadata.price"},
                    "transaction_count": {"$sum": 1},
                    "avg_price": {"$avg": "$metadata.price"}
                }
            },
            {
                "$sort": {"total_revenue": -1}
            }
        ]

        result = list(self.collection.aggregate(pipeline))
        return {item["_id"]: item for item in result}


# ============================================================================
# GEOSPATIAL QUERIES
# ============================================================================

class GeoLocationManager:
    """Handle geospatial queries."""

    def __init__(self, db):
        self.collection = db.events if db else None

    def find_events_near_location(
        self,
        longitude: float,
        latitude: float,
        max_distance: int = 5000  # meters
    ) -> List[Dict]:
        """
        Find events near a geographic location.
        Requires geospatial index on geo.coordinates.
        """
        if not self.collection:
            return []

        return list(self.collection.find({
            "geo.coordinates": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": max_distance
                }
            }
        }))


# ============================================================================
# BATCH PROCESSING & OPTIMIZATION
# ============================================================================

class DataProcessor:
    """Process data efficiently for analytics."""

    def __init__(self, db):
        self.db = db

    def calculate_cohort_metrics(self) -> Dict:
        """
        Calculate metrics by registration cohort.
        Use case: Retention analysis, user lifecycle.
        """
        if not self.db:
            return {}

        pipeline = [
            {
                "$project": {
                    "user_id": "$_id",
                    "cohort": {
                        "$dateToString": {
                            "format": "%Y-%m",
                            "date": "$created_at"
                        }
                    },
                    "engagement": "$metrics.avg_engagement_score"
                }
            },
            {
                "$group": {
                    "_id": "$cohort",
                    "user_count": {"$sum": 1},
                    "avg_engagement": {"$avg": "$engagement"}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        result = list(self.db.users.aggregate(pipeline))
        return {item["_id"]: item for item in result}

    def export_data_for_analysis(self, query: Dict, batch_size: int = 1000) -> None:
        """
        Export data in batches for analysis.
        Use case: Data science pipeline, bulk processing.
        """
        if not self.db:
            return

        collection = self.db.events
        skip = 0
        batch_num = 0

        while True:
            documents = list(collection.find(query).skip(skip).limit(batch_size))

            if not documents:
                break

            # Process batch (write to file, send to ML model, etc.)
            logger.info(f"Processing batch {batch_num} with {len(documents)} documents")

            # Example: could write to JSON for external processing
            # with open(f"batch_{batch_num}.json", "w") as f:
            #     json.dump(documents, f, default=str)

            batch_num += 1
            skip += batch_size


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def demonstrate_mongodb():
    """Demonstrate MongoDB advanced patterns."""

    logger.info("\n" + "="*80)
    logger.info("MongoDB - Advanced Patterns Demonstration")
    logger.info("="*80 + "\n")

    # Initialize
    mongo_manager = MongoDBManager()

    if mongo_manager.db is None:
        logger.warning("MongoDB not available - showing structure examples only")
        logger.info("\nExample User Document:")
        pprint(USER_PROFILE_EXAMPLE)
        logger.info("\nExample Event Document:")
        pprint(EVENT_EXAMPLE)
        return

    mongo_manager.create_collections_with_schema()

    # Create managers
    user_manager = UserManager(mongo_manager.db)
    event_tracker = EventTracker(mongo_manager.db)
    data_processor = DataProcessor(mongo_manager.db)

    # [1] Insert sample users
    logger.info("\n[1] Inserting sample users...")
    sample_users = [
        {
            "username": f"data_scientist_{i}",
            "email": f"ds_{i}@example.com",
            "created_at": datetime.utcnow() - timedelta(days=30*i),
            "profile": {
                "interests": ["data-science", "python", "ml"],
                "expertise_level": "senior",
                "total_projects": 10 + i
            },
            "metrics": {
                "last_active": datetime.utcnow(),
                "total_views": 100 * i,
                "avg_engagement_score": 7.0 + i
            }
        }
        for i in range(1, 4)
    ]

    user_manager.bulk_insert_users(sample_users)

    # [2] Log sample events
    logger.info("\n[2] Logging sample events...")
    for _ in range(5):
        event_tracker.log_event({
            "user_id": 1,
            "event_type": "user_purchase",
            "metadata": {
                "product_id": "PROD-001",
                "price": 99.99,
                "category": "electronics"
            },
            "geo": {
                "country": "Ukraine",
                "city": "Kyiv"
            }
        })

    # [3] Query users by interest
    logger.info("\n[3] Users interested in 'data-science':")
    data_science_users = user_manager.find_users_by_interest("data-science")
    for user in data_science_users:
        logger.info(f"  - {user.get('username')}")

    # [4] Event distribution
    logger.info("\n[4] Event Distribution:")
    distribution = event_tracker.get_event_distribution()
    for event_type, count in distribution.items():
        logger.info(f"  - {event_type}: {count}")

    # [5] User activity metrics
    logger.info("\n[5] Top Active Users:")
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    activity = event_tracker.get_user_activity_metrics(start_date, end_date)
    for user_activity in activity[:5]:
        logger.info(f"  - User {user_activity['_id']}: {user_activity['event_count']} events")

    # [6] Purchase analytics
    logger.info("\n[6] Purchase Analytics by Category:")
    purchase_data = event_tracker.get_purchase_analytics()
    for category, metrics in purchase_data.items():
        logger.info(f"  - {category}: Revenue={metrics['total_revenue']:.2f}$, Transactions={metrics['transaction_count']}")

    logger.info("\n" + "="*80)
    logger.info("✓ MongoDB demonstration completed")
    logger.info("="*80 + "\n")

    mongo_manager.close()


if __name__ == "__main__":
    demonstrate_mongodb()
