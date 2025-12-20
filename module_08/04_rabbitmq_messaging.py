"""
Module 8.4: RabbitMQ Message Broker - Async Processing
=======================================================

Asynchronous task processing with RabbitMQ:
- Producer-Consumer architecture
- Message queue patterns
- Task retry mechanisms
- Dead letter queues (DLQ)
- Monitoring and logging
- Real-world use cases: data processing, notifications, analytics

Author: Senior Data Science Engineer
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import traceback

# Try to import pika (RabbitMQ Python client)
try:
    import pika
    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pika not available - install with: pip install pika")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

RABBITMQ_CONFIG = {
    "host": "localhost",
    "port": 5672,
    "username": "guest",
    "password": "guest",
    "virtual_host": "/"
}

# Exchange and Queue configuration
EXCHANGES = {
    "data_processing": {"type": "direct", "durable": True},
    "notifications": {"type": "topic", "durable": True},
    "analytics": {"type": "fanout", "durable": True},
}

QUEUES = {
    "user_data_processing": {"durable": True, "arguments": {"x-max-priority": 10}},
    "email_notifications": {"durable": True},
    "sms_notifications": {"durable": True},
    "analytics_events": {"durable": True},
    "user_data_processing_dlq": {"durable": True},  # Dead Letter Queue
}

BINDINGS = [
    ("data_processing", "user_data_processing", "process_user"),
    ("notifications", "email_notifications", "notify.email.*"),
    ("notifications", "sms_notifications", "notify.sms.*"),
    ("analytics", "analytics_events", ""),
]


# ============================================================================
# MESSAGE MODELS
# ============================================================================

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 5
    HIGH = 10


@dataclass
class Message:
    """Base message class."""
    id: str
    type: str
    payload: Dict[str, Any]
    timestamp: str
    priority: int = MessagePriority.NORMAL.value
    retry_count: int = 0
    max_retries: int = 3

    def to_json(self) -> str:
        """Convert message to JSON."""
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create message from JSON."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class UserDataMessage(Message):
    """Message for user data processing."""
    pass


@dataclass
class NotificationMessage(Message):
    """Message for notifications."""
    recipient: str = ""
    subject: str = ""
    content: str = ""


@dataclass
class AnalyticsMessage(Message):
    """Message for analytics events."""
    event_type: str = ""
    user_id: int = 0
    properties: Dict = None


# ============================================================================
# RABBITMQ CONNECTION MANAGEMENT
# ============================================================================

class RabbitMQConnection:
    """Manage RabbitMQ connection and channels."""

    def __init__(self, config: Dict[str, Any] = RABBITMQ_CONFIG):
        self.config = config
        self.connection = None
        self.channel = None

    def connect(self) -> bool:
        """Establish connection to RabbitMQ."""
        if not RABBITMQ_AVAILABLE:
            logger.warning("RabbitMQ not available")
            return False

        try:
            credentials = pika.PlainCredentials(
                self.config["username"],
                self.config["password"]
            )
            parameters = pika.ConnectionParameters(
                host=self.config["host"],
                port=self.config["port"],
                virtual_host=self.config["virtual_host"],
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2
            )

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            logger.info("✓ Connected to RabbitMQ")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to connect to RabbitMQ: {str(e)}")
            return False

    def setup_infrastructure(self) -> None:
        """Declare exchanges, queues, and bindings."""
        if not self.channel:
            logger.warning("Not connected to RabbitMQ")
            return

        # Declare exchanges
        for exchange_name, exchange_config in EXCHANGES.items():
            self.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_config["type"],
                durable=exchange_config["durable"]
            )
            logger.info(f"✓ Declared exchange: {exchange_name}")

        # Declare queues
        for queue_name, queue_config in QUEUES.items():
            self.channel.queue_declare(
                queue=queue_name,
                durable=queue_config["durable"],
                arguments=queue_config.get("arguments")
            )
            logger.info(f"✓ Declared queue: {queue_name}")

        # Create bindings
        for exchange, queue, routing_key in BINDINGS:
            self.channel.queue_bind(
                exchange=exchange,
                queue=queue,
                routing_key=routing_key
            )
            logger.info(f"✓ Bound queue {queue} to exchange {exchange}")

    def close(self) -> None:
        """Close connection."""
        if self.connection:
            self.connection.close()
            logger.info("RabbitMQ connection closed")


# ============================================================================
# PRODUCER
# ============================================================================

class Producer:
    """Publish messages to RabbitMQ."""

    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection
        self.channel = connection.channel

    def publish_message(
        self,
        exchange: str,
        routing_key: str,
        message: Message,
        priority: int = MessagePriority.NORMAL.value
    ) -> bool:
        """Publish message to exchange."""
        if not self.channel:
            logger.warning("Channel not available")
            return False

        try:
            properties = pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  # Persistent
                priority=priority,
                message_id=message.id,
                timestamp=int(datetime.utcnow().timestamp())
            )

            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message.to_json(),
                properties=properties
            )

            logger.info(f"✓ Published message {message.id} to {exchange}")
            return True

        except Exception as e:
            logger.error(f"✗ Error publishing message: {str(e)}")
            return False

    def publish_user_data_event(self, user_id: int, data: Dict) -> bool:
        """Publish user data processing event."""
        message = UserDataMessage(
            id=str(uuid.uuid4()),
            type="user_data",
            payload={"user_id": user_id, **data},
            timestamp=datetime.utcnow().isoformat()
        )

        return self.publish_message(
            exchange="data_processing",
            routing_key="process_user",
            message=message,
            priority=MessagePriority.HIGH.value
        )

    def publish_notification(
        self,
        channel: str,
        recipient: str,
        subject: str,
        content: str
    ) -> bool:
        """Publish notification event."""
        message = NotificationMessage(
            id=str(uuid.uuid4()),
            type="notification",
            payload={"channel": channel},
            timestamp=datetime.utcnow().isoformat(),
            recipient=recipient,
            subject=subject,
            content=content
        )

        routing_key = f"notify.{channel}.{recipient.split('@')[0]}"

        return self.publish_message(
            exchange="notifications",
            routing_key=routing_key,
            message=message
        )

    def publish_analytics_event(
        self,
        event_type: str,
        user_id: int,
        properties: Dict
    ) -> bool:
        """Publish analytics event."""
        message = AnalyticsMessage(
            id=str(uuid.uuid4()),
            type="analytics",
            payload={"event_type": event_type, "user_id": user_id},
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            user_id=user_id,
            properties=properties
        )

        return self.publish_message(
            exchange="analytics",
            routing_key="",  # Fanout
            message=message
        )


# ============================================================================
# CONSUMER
# ============================================================================

class Consumer(ABC):
    """Base consumer for processing messages."""

    def __init__(self, connection: RabbitMQConnection, queue_name: str):
        self.connection = connection
        self.channel = connection.channel
        self.queue_name = queue_name
        self.processed_count = 0
        self.error_count = 0

    @abstractmethod
    def process_message(self, message: Message) -> bool:
        """Process a message - implement in subclasses."""
        pass

    def message_callback(self, ch, method, properties, body: bytes) -> None:
        """Callback for processing messages."""
        try:
            # Parse message
            message = Message.from_json(body.decode())
            logger.info(f"Processing message {message.id}")

            # Process
            success = self.process_message(message)

            if success:
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                self.processed_count += 1
                logger.info(f"✓ Message {message.id} processed")
            else:
                # Handle retry
                if message.retry_count < message.max_retries:
                    message.retry_count += 1
                    logger.warning(f"Retrying message {message.id} ({message.retry_count}/{message.max_retries})")

                    # Republish with retry count
                    self.channel.basic_publish(
                        exchange="",
                        routing_key=self.queue_name,
                        body=message.to_json(),
                        properties=properties
                    )
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    # Send to DLQ
                    logger.error(f"Max retries exceeded for message {message.id}")
                    self.channel.basic_publish(
                        exchange="",
                        routing_key=f"{self.queue_name}_dlq",
                        body=message.to_json(),
                        properties=properties
                    )
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    self.error_count += 1

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            logger.error(traceback.format_exc())
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self, prefetch_count: int = 1) -> None:
        """Start consuming messages."""
        if not self.channel:
            logger.warning("Channel not available")
            return

        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.message_callback
        )

        logger.info(f"✓ Started consuming from {self.queue_name}")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
            logger.info(f"Consumer stopped. Processed: {self.processed_count}, Errors: {self.error_count}")


# ============================================================================
# CONCRETE CONSUMERS
# ============================================================================

class UserDataConsumer(Consumer):
    """Consumer for user data processing."""

    def process_message(self, message: Message) -> bool:
        """Process user data."""
        try:
            user_id = message.payload.get("user_id")
            logger.info(f"  Processing user {user_id} data...")

            # Simulate data processing
            time.sleep(0.5)

            # Example: validate user data
            if user_id and user_id > 0:
                logger.info(f"  ✓ User {user_id} data validated")
                return True
            else:
                logger.error(f"  ✗ Invalid user ID: {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error processing user data: {str(e)}")
            return False


class NotificationConsumer(Consumer):
    """Consumer for sending notifications."""

    def process_message(self, message: Message) -> bool:
        """Send notification."""
        try:
            if message.type != "notification":
                return False

            recipient = getattr(message, 'recipient', '')
            subject = getattr(message, 'subject', '')
            content = getattr(message, 'content', '')

            logger.info(f"  Sending notification to {recipient}")
            logger.info(f"  Subject: {subject}")

            # Simulate sending
            time.sleep(0.3)

            logger.info(f"  ✓ Notification sent")
            return True

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False


class AnalyticsConsumer(Consumer):
    """Consumer for analytics event processing."""

    def __init__(self, connection: RabbitMQConnection, queue_name: str):
        super().__init__(connection, queue_name)
        self.events_buffer = []
        self.batch_size = 10

    def process_message(self, message: Message) -> bool:
        """Process analytics event."""
        try:
            if message.type != "analytics":
                return False

            event_type = getattr(message, 'event_type', '')
            user_id = getattr(message, 'user_id', 0)

            logger.info(f"  Recording analytics event: {event_type} for user {user_id}")

            # Buffer events for batch processing
            self.events_buffer.append({
                "event_type": event_type,
                "user_id": user_id,
                "timestamp": message.timestamp
            })

            # Process batch if reached size
            if len(self.events_buffer) >= self.batch_size:
                self.process_batch()

            return True

        except Exception as e:
            logger.error(f"Error processing analytics event: {str(e)}")
            return False

    def process_batch(self) -> None:
        """Process buffered events in batch."""
        if self.events_buffer:
            logger.info(f"  Processing batch of {len(self.events_buffer)} events")
            # Simulate batch analytics processing
            time.sleep(0.2)
            logger.info(f"  ✓ Batch processed")
            self.events_buffer.clear()


# ============================================================================
# REAL-WORLD USE CASES
# ============================================================================

class UserDataPipeline:
    """Real-world use case: User data processing pipeline."""

    def __init__(self, producer: Producer):
        self.producer = producer

    def process_user_signup(self, user_id: int, user_data: Dict) -> None:
        """
        Trigger async processing on user signup.
        Use case: Data validation, enrichment, ML features extraction.
        """
        logger.info(f"[SIGNUP] Queueing processing for user {user_id}")

        self.producer.publish_user_data_event(user_id, {
            **user_data,
            "event": "signup",
            "ip_address": user_data.get("ip_address"),
            "device": user_data.get("device")
        })

    def process_user_purchase(self, user_id: int, purchase_data: Dict) -> None:
        """
        Trigger async processing on purchase.
        Use case: Fraud detection, recommendation update, inventory.
        """
        logger.info(f"[PURCHASE] Queueing processing for user {user_id}")

        self.producer.publish_user_data_event(user_id, {
            **purchase_data,
            "event": "purchase"
        })

        # Also trigger analytics
        self.producer.publish_analytics_event(
            event_type="purchase",
            user_id=user_id,
            properties={
                "amount": purchase_data.get("amount"),
                "category": purchase_data.get("category")
            }
        )


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def demonstrate_rabbitmq():
    """Demonstrate RabbitMQ patterns."""

    logger.info("\n" + "="*80)
    logger.info("RabbitMQ - Message Broker & Async Processing")
    logger.info("="*80 + "\n")

    if not RABBITMQ_AVAILABLE:
        logger.error("pika not installed. Install with: pip install pika")
        logger.info("\nExample Message Structure:")
        logger.info(json.dumps({
            "id": "msg-uuid-123",
            "type": "user_data",
            "payload": {"user_id": 123, "action": "process"},
            "timestamp": "2024-01-15T10:30:00",
            "priority": 5
        }, indent=2))
        return

    # Initialize connection
    rabbitmq = RabbitMQConnection(RABBITMQ_CONFIG)

    if not rabbitmq.connect():
        logger.error("Could not connect to RabbitMQ")
        logger.info("Make sure RabbitMQ is running:")
        logger.info("  Local: docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:latest")
        return

    # Setup infrastructure
    rabbitmq.setup_infrastructure()

    # Create producer
    producer = Producer(rabbitmq)

    # ---- DEMONSTRATIONS ----

    logger.info("[1] Publishing User Data Events")
    logger.info("-" * 80)

    pipeline = UserDataPipeline(producer)

    # Simulate user signup
    pipeline.process_user_signup(
        user_id=123,
        user_data={
            "username": "data_scientist",
            "email": "ds@example.com",
            "ip_address": "192.168.1.1",
            "device": "mobile"
        }
    )

    # Simulate user purchase
    pipeline.process_user_purchase(
        user_id=123,
        purchase_data={
            "product_id": "PROD-001",
            "amount": 99.99,
            "category": "electronics"
        }
    )

    logger.info("\n[2] Publishing Notifications")
    logger.info("-" * 80)

    producer.publish_notification(
        channel="email",
        recipient="user@example.com",
        subject="Welcome to our platform",
        content="Thank you for signing up!"
    )

    producer.publish_notification(
        channel="sms",
        recipient="+380951234567",
        subject="",
        content="Your verification code: 123456"
    )

    logger.info("\n[3] Publishing Analytics Events")
    logger.info("-" * 80)

    for i in range(5):
        producer.publish_analytics_event(
            event_type="page_view",
            user_id=123,
            properties={
                "page": f"/page-{i}",
                "duration_seconds": 10 + i*5
            }
        )

    logger.info("\n[4] Consumer Statistics (if running)")
    logger.info("-" * 80)
    logger.info("To process messages, run separate consumer scripts:")
    logger.info("  - User Data Consumer: python04_rabbitmq_messaging.py --consumer=user_data")
    logger.info("  - Notification Consumer: python04_rabbitmq_messaging.py --consumer=notification")
    logger.info("  - Analytics Consumer: python04_rabbitmq_messaging.py --consumer=analytics")

    logger.info("\n[5] Message Queue Information")
    logger.info("-" * 80)

    if rabbitmq.channel:
        for queue_name in QUEUES.keys():
            try:
                method = rabbitmq.channel.queue_declare(
                    queue=queue_name,
                    passive=True  # Don't create if doesn't exist
                )
                logger.info(f"  {queue_name}: {method.method.message_count} messages")
            except:
                pass

    logger.info("\n" + "="*80)
    logger.info("✓ RabbitMQ demonstration completed")
    logger.info("="*80 + "\n")

    rabbitmq.close()


if __name__ == "__main__":
    demonstrate_rabbitmq()
