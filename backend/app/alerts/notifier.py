"""
Worker that turns price-alert messages into emails:  python -m app.alerts.notifier

Messages are acknowledged only after the email is sent, so a crash or an SMTP outage leaves them in the queue.
"""

import logging
import smtplib
import time
from collections.abc import Callable
from email.message import EmailMessage

from app.alerts.events import AlertEvent
from app.alerts.queue import QUEUE, connect
from app.core.config import settings

logger = logging.getLogger(__name__)
Mailer = Callable[[str, str, str], None]
# Without a pause a message that keeps failing is redelivered instantly, spinning the worker and the broker.
RETRY_DELAY_SECONDS = 5


def handle_event(event: AlertEvent, send: Mailer) -> None:
    subject = f"ירידת מחיר: {event.name}"
    body = (
        f"{event.name} ירד מ-₪{event.previous_price:.2f} ל-₪{event.price:.2f}\n"
        f"ב{event.chain}, סניף {event.store}.\n\n"
        "קיבלת את ההודעה כי הגדרת התראת מחיר ב-SalSmart."
    )
    send(event.email, subject, body)


def smtp_send(to: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = settings.ALERT_FROM, to, subject
    message.set_content(body)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as smtp:
        if settings.SMTP_USER:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(message)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    channel = connect(settings.RABBITMQ_URL).channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.basic_qos(prefetch_count=10)

    def on_message(ch, method, _properties, body: bytes) -> None:  # type: ignore[no-untyped-def]
        event = AlertEvent.from_json(body)
        try:
            handle_event(event, smtp_send)
        except (OSError, smtplib.SMTPException):
            logger.exception("Email for alert %s failed; returning it to the queue", event.alert_id)
            time.sleep(RETRY_DELAY_SECONDS)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return
        logger.info("Sent alert %s to %s", event.alert_id, event.email)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)
    logger.info("Waiting for price alerts on %s", QUEUE)
    channel.start_consuming()


if __name__ == "__main__":
    main()
