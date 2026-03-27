"""Background IMAP polling for audit report requests."""
from __future__ import annotations

import email
import imaplib
import logging
import threading
import unicodedata
from datetime import datetime
from email.utils import parseaddr
from email.message import Message

from PyQt5.QtCore import QObject, QTimer

from config import settings
from database.sales_db import SalesDB
from hardware.email_notifier import send_email

logger = logging.getLogger(__name__)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    return without_marks.casefold().strip()


def _compact_text(value: str) -> str:
    return "".join(char for char in _normalize_text(value) if char.isalnum())


def _subject_matches_system_name(subject: str) -> bool:
    return _compact_text(subject) == _compact_text(settings.SYSTEM_NAME)


def _body_requests_audit(body: str) -> bool:
    normalized_body = _normalize_text(body)
    compact_body = _compact_text(body)
    keyword = _normalize_text(settings.AUDIT_EMAIL_BODY_KEYWORD)
    compact_keyword = _compact_text(settings.AUDIT_EMAIL_BODY_KEYWORD)

    if compact_keyword and compact_keyword in compact_body:
        return True
    if "auditoria" in compact_body:
        return True
    return normalized_body in {"a", "auditoria", "auditorias"}


def generate_audit_report(sales_db: SalesDB) -> str:
    sales = sales_db.fetch_sales()
    rinse_events = sales_db.fetch_rinse_events()
    email_events = sales_db.fetch_email_events("out_of_service")

    total_served = sum(float(row["volume"]) for row in sales)
    total_ingreso = sum(float(row["payment_received"]) for row in sales)
    total_cobro = sum(float(row["price"]) for row in sales)
    total_egreso = sum(max(0.0, float(row["payment_received"]) - float(row["price"])) for row in sales)
    total_rinse_liters = sum(float(row["liters"]) for row in rinse_events)
    total_water_used = total_served + total_rinse_liters

    product_lines = []
    for product in settings.PRODUCTS:
        product_sales = [row for row in sales if row["product"] == product["name"]]
        product_lines.append(
            f"- {product['name']}: {len(product_sales)} ventas, "
            f"{sum(float(row['volume']) for row in product_sales):.2f} L, "
            f"${sum(float(row['price']) for row in product_sales):.2f}"
        )

    recent_sales = []
    for row in sales[:15]:
        recent_sales.append(
            f"- {str(row['timestamp']).replace('T', ' ')} | {row['product']} | "
            f"{float(row['volume']):.2f} L | ingreso ${float(row['payment_received']):.2f} | "
            f"cobro ${float(row['price']):.2f}"
        )

    report_lines = [
        "Reporte de Auditoria",
        "",
        f"Sistema: {settings.SYSTEM_NAME}",
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Resumen general:",
        f"- Total agua servida: {total_served:.2f} L",
        f"- Total enjuague: {total_rinse_liters:.2f} L",
        f"- Total agua usada: {total_water_used:.2f} L",
        f"- Total ingreso: ${total_ingreso:.2f}",
        f"- Total cobrado: ${total_cobro:.2f}",
        f"- Total egreso: -${total_egreso:.2f}",
        f"- Total ventas: {len(sales)}",
        f"- Correos por falta de agua: {sum(1 for row in email_events if row['status'] == 'sent')}",
        "",
        "Ventas por producto:",
        *(product_lines or ["- Sin ventas registradas"]),
        "",
        "Ventas recientes:",
        *(recent_sales or ["- Sin ventas registradas"]),
    ]
    return "\n".join(report_lines)


def _extract_text_body(message: Message) -> str:
    if message.is_multipart():
        parts: list[str] = []
        for part in message.walk():
            if part.get_content_type() != "text/plain":
                continue
            if part.get_content_disposition() == "attachment":
                continue
            payload = part.get_payload(decode=True) or b""
            charset = part.get_content_charset() or "utf-8"
            try:
                parts.append(payload.decode(charset, errors="ignore"))
            except Exception:
                parts.append(payload.decode("utf-8", errors="ignore"))
        return "\n".join(parts)
    payload = message.get_payload(decode=True) or b""
    charset = message.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="ignore")
    except Exception:
        return payload.decode("utf-8", errors="ignore")


class AuditEmailService(QObject):
    def __init__(self, sales_db: SalesDB, parent=None):
        super().__init__(parent)
        self.sales_db = sales_db
        self._polling = False
        self._timer = QTimer(self)
        self._timer.setInterval(settings.AUDIT_EMAIL_POLL_MS)
        self._timer.timeout.connect(self.poll_now)

    def start(self) -> None:
        self._timer.start()
        self.poll_now()

    def stop(self) -> None:
        self._timer.stop()

    def poll_now(self) -> None:
        if self._polling:
            return
        self._polling = True
        thread = threading.Thread(target=self._poll_worker, daemon=True, name="audit-email-poller")
        thread.start()

    def _poll_worker(self) -> None:
        try:
            self.check_incoming_emails()
        except Exception:
            logger.exception("Failed to poll incoming audit emails")
        finally:
            self._polling = False

    def check_incoming_emails(self) -> None:
        if not settings.IMAP_HOST or not settings.IMAP_USERNAME or not settings.IMAP_PASSWORD:
            return

        mailbox = None
        try:
            if settings.IMAP_USE_SSL:
                mailbox = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
            else:
                mailbox = imaplib.IMAP4(settings.IMAP_HOST, settings.IMAP_PORT)
            mailbox.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)
            mailbox.select(settings.AUDIT_EMAIL_INBOX)
            status, data = mailbox.search(None, "UNSEEN")
            if status != "OK":
                return
            for message_id in data[0].split():
                self._process_message(mailbox, message_id)
        finally:
            if mailbox is not None:
                try:
                    mailbox.close()
                except Exception:
                    pass
                try:
                    mailbox.logout()
                except Exception:
                    pass

    def _process_message(self, mailbox, message_id: bytes) -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        status, data = mailbox.fetch(message_id, "(RFC822)")
        if status != "OK" or not data or not data[0]:
            return
        raw_message = data[0][1]
        message = email.message_from_bytes(raw_message)
        subject = str(message.get("Subject", "")).strip()
        body = _extract_text_body(message)
        sender = parseaddr(message.get("From", ""))[1].strip().lower()
        mailbox.store(message_id, "+FLAGS", "\\Seen")

        if not _subject_matches_system_name(subject):
            logger.info("Ignoring audit email from %s due to subject mismatch: %s", sender, subject)
            self.sales_db.log_email_event(timestamp, "audit_request", sender, subject, "ignored_subject")
            return
        if not _body_requests_audit(body):
            logger.info("Ignoring audit email from %s due to missing body keyword", sender)
            self.sales_db.log_email_event(timestamp, "audit_request", sender, subject, "ignored_body")
            return

        allowed = settings.authorized_audit_emails()
        if allowed and sender not in allowed:
            logger.warning("Unauthorized audit email request from %s", sender)
            self.sales_db.log_email_event(timestamp, "audit_request", sender, subject, "unauthorized")
            return

        logger.info("Audit email request received from %s", sender)
        self.sales_db.log_email_event(timestamp, "audit_request", sender, subject, "received")
        report = generate_audit_report(self.sales_db)
        sent = False
        try:
            sent = send_email(
                recipient=sender,
                subject=f"Reporte de Auditoría - {settings.SYSTEM_NAME}",
                body=report,
            )
        except Exception:
            logger.exception("Failed to send audit report to %s", sender)
        self.sales_db.log_email_event(
            timestamp,
            "audit_report",
            sender,
            "Reporte de Auditoría",
            "sent" if sent else "failed",
        )
