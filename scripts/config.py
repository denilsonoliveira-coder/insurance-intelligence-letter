"""Configuracoes centrais do projeto."""

from __future__ import annotations

import os
from dataclasses import dataclass

RSS_FEEDS: list[str] = [
    "https://www.sonhoseguro.com.br/feed/",
    "https://cqcs.com.br/feed/",
]

NEWS_LIMIT: int = int(os.getenv("NEWS_LIMIT", "20"))
NEWSLETTER_NAME: str = "Insurance Intelligence Letter"
EMAIL_SUBJECT_PREFIX: str = NEWSLETTER_NAME
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")


@dataclass(frozen=True)
class SmtpSettings:
    """Parametros de conexao SMTP."""

    host: str
    port: int
    use_starttls: bool = True


def get_smtp_settings(email_user: str) -> SmtpSettings:
    """Resolve o provedor SMTP pelo dominio ou por sobrescrita via ambiente."""
    custom_host = os.getenv("SMTP_HOST")
    custom_port = os.getenv("SMTP_PORT")
    if custom_host:
        return SmtpSettings(
            host=custom_host,
            port=int(custom_port or "587"),
            use_starttls=os.getenv("SMTP_STARTTLS", "true").lower() == "true",
        )

    domain = email_user.rsplit("@", maxsplit=1)[-1].lower()
    if domain in {"gmail.com", "googlemail.com"}:
        return SmtpSettings("smtp.gmail.com", 587)
    if domain in {"outlook.com", "hotmail.com", "live.com", "msn.com"}:
        return SmtpSettings("smtp-mail.outlook.com", 587)
    return SmtpSettings("smtp.office365.com", 587)
