import json
import os
import time
from typing import Dict, Iterable

import pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "user_events")
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")


def get_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    return pika.BlockingConnection(params)


def publish_events(events: Iterable[Dict]) -> None:
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    for event in events:
        payload = json.dumps(event)
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=payload,
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
        print("Sent", payload)
        time.sleep(0.2)

    connection.close()


def fake_user_events() -> list[Dict]:
    return [
        {"event": "user.created", "external_id": "u10", "full_name": "Async UA", "email": "async@example.com", "country_code": "UA"},
        {"event": "user.created", "external_id": "u11", "full_name": "Stream PL", "email": "stream@example.com", "country_code": "PL"},
        {"event": "user.updated", "external_id": "u1", "full_name": "Ivan Petrenko", "email": "ivan@example.com", "country_code": "UA"},
    ]


if __name__ == "__main__":
    try:
        publish_events(fake_user_events())
    except Exception as exc:  # pragma: no cover - демо сценарій
        print("RabbitMQ is not reachable. Run docker-compose up or point env vars to a broker.")
        print(exc)
