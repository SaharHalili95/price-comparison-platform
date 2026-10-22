"""RabbitMQ plumbing. The ingestion only publishes; the notifier consumes, so email trouble never slows ingestion."""

import pika

QUEUE = "price-alerts"


def connect(url: str) -> pika.BlockingConnection:
    return pika.BlockingConnection(pika.URLParameters(url))


def publish(url: str, payloads: list[bytes]) -> None:
    connection = connect(url)
    try:
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE, durable=True)
        for payload in payloads:
            channel.basic_publish(
                exchange="", routing_key=QUEUE, body=payload,
                properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent, content_type="application/json"),
            )
    finally:
        connection.close()
