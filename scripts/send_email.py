"""Envia a newsletter HTML por SMTP."""

from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

from config import EMAIL_SUBJECT_PREFIX, NEWSLETTER_NAME, get_smtp_settings

BASE_DIR = Path(__file__).resolve().parents[1]
LETTER_FILE = BASE_DIR / "output" / "letter.html"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def require_env(name: str) -> str:
    """Le uma variavel obrigatoria ou interrompe com mensagem objetiva."""
    value = os.getenv(name, "").strip()
    if not value:
        raise EnvironmentError(f"A variavel {name} nao foi definida.")
    return value


def parse_recipients(raw: str) -> list[str]:
    """Aceita um ou varios destinatarios separados por virgula ou ponto e virgula."""
    normalized = raw.replace(";", ",")
    recipients = [item.strip() for item in normalized.split(",") if item.strip()]
    if not recipients:
        raise ValueError("EMAIL_TO nao contem destinatarios validos.")
    return recipients


def build_message(sender: str, recipients: list[str], html: str) -> EmailMessage:
    """Cria uma mensagem multipart com fallback em texto simples."""
    current_date = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")
    message = EmailMessage()
    message["Subject"] = f"{EMAIL_SUBJECT_PREFIX} - {current_date}"
    message["From"] = f"{NEWSLETTER_NAME} <{sender}>"
    message["To"] = ", ".join(recipients)
    message.set_content(
        "Sua newsletter foi gerada em HTML. Abra este e-mail em um cliente "
        "compatível para visualizar o conteúdo completo."
    )
    message.add_alternative(html, subtype="html")
    return message


def main() -> None:
    """Le as credenciais, conecta ao SMTP e envia a mensagem."""
    sender = require_env("EMAIL_USER")
    password = require_env("EMAIL_PASSWORD")
    recipients = parse_recipients(require_env("EMAIL_TO"))
    if not LETTER_FILE.exists():
        raise FileNotFoundError(f"Newsletter nao encontrada: {LETTER_FILE}")

    html = LETTER_FILE.read_text(encoding="utf-8")
    message = build_message(sender, recipients, html)
    settings = get_smtp_settings(sender)
    LOGGER.info("Conectando a %s:%d", settings.host, settings.port)

    with smtplib.SMTP(settings.host, settings.port, timeout=30) as smtp:
        smtp.ehlo()
        if settings.use_starttls:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(sender, password)
        smtp.send_message(message)

    LOGGER.info("Newsletter enviada para %d destinatario(s).", len(recipients))


if __name__ == "__main__":
    main()
