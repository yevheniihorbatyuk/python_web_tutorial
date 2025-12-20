import json
import os
from typing import Any, Dict

import pika
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "user_events")
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "geo_users")


def get_channel() -> pika.adapters.blocking_connection.BlockingChannel:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=10)
    return channel


def get_users_collection():
    client = MongoClient(MONGO_URI)
    col = client[MONGO_DB].users_events
    col.create_index("external_id", unique=True)
    return col


def handle_message(event: Dict[str, Any]) -> None:
    external_id = event.get("external_id")
    if not external_id:
        return
    payload = {
        "external_id": external_id,
        "full_name": event.get("full_name"),
        "email": event.get("email"),
        "country_code": event.get("country_code"),
        "source_event": event.get("event"),
    }
    # Idempotent upsert — однакова подія не створить дублікат
    users = get_users_collection()
    users.update_one({"external_id": external_id}, {"$set": payload}, upsert=True)


def main() -> None:
    channel = get_channel()

    def on_message(_ch, method, properties, body):
        try:
            event = json.loads(body.decode())
            handle_message(event)
            print("Saved", event)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:  # pragma: no cover - демонстраційний лог
            print("Failed to process message", exc)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=on_message)
    print("[consumer] Waiting for messages. Press CTRL+C to exit.")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # pragma: no cover
        print("Stopped by user")
    except Exception as exc:  # pragma: no cover
        print("RabbitMQ or MongoDB not reachable. Start docker-compose or adjust env vars.")
        print(exc)
