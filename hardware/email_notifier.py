"""Background email notifications for vending alerts."""
from __future__ import annotations

import logging
import smtplib
import ssl
import threading
from email.message import EmailMessage

from config import settings

logger = logging.getLogger(__name__)


def send_async_email(*, recipient: str, subject: str, body: str) -> bool:
    recipient = (recipient or "").strip()
    if not recipient:
        logger.warning("No recipient configured for alert email")
        return False
    if not settings.SMTP_HOST or not settings.SMTP_FROM:
        logger.warning("SMTP settings are incomplete; skipping alert email")
        return False

    thread = threading.Thread(
        target=_send_email,
        kwargs={
            "recipient": recipient,
            "subject": subject,
            "body": body,
        },
        daemon=True,
        name="email-notifier",
    )
    thread.start()
    return True


def _send_email(*, recipient: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    try:
        if settings.SMTP_USE_TLS:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls(context=ssl.create_default_context())
                if settings.SMTP_USERNAME:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                if settings.SMTP_USERNAME:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
        logger.info("Out-of-service alert email sent to %s", recipient)
    except Exception:
        logger.exception("Failed to send out-of-service alert email")
