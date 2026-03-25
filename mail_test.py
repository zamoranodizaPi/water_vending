"""Simple SMTP test script for manual email verification."""
from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = os.getenv("VENDING_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("VENDING_SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("VENDING_SMTP_USERNAME", "zamoranodiza@gmail.com")
SMTP_PASSWORD = os.getenv("VENDING_SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("VENDING_SMTP_FROM", SMTP_USERNAME)
SMTP_TO = os.getenv("VENDING_SMTP_TO", SMTP_USERNAME)


def main():
    if not SMTP_PASSWORD:
        raise SystemExit("Falta VENDING_SMTP_PASSWORD")

    msg = EmailMessage()
    msg["Subject"] = "Prueba"
    msg["From"] = SMTP_FROM
    msg["To"] = SMTP_TO
    msg.set_content("Este es un test de SMTP.")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

    print("Correo enviado con exito")


if __name__ == "__main__":
    main()
