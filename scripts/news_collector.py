"""Coleta noticias de feeds RSS e salva as mais recentes em JSON."""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import feedparser
from bs4 import BeautifulSoup

from config import NEWS_LIMIT, RSS_FEEDS

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BASE_DIR / "output" / "news.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def clean_html(value: str | None) -> str:
    """Converte HTML do feed em texto simples e normaliza espacos."""
    if not value:
        return ""
    text = BeautifulSoup(value, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def parse_entry_date(entry: Any) -> datetime:
    """Extrai a data da entrada e sempre devolve um datetime com timezone."""
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        value = entry.get(field)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)

    for field in ("published", "updated", "created"):
        value = entry.get(field)
        if value:
            try:
                parsed = parsedate_to_datetime(value)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
            except (TypeError, ValueError, OverflowError):
                LOGGER.debug("Data invalida no campo %s: %s", field, value)

    return datetime.now(timezone.utc)


def collect_feed(feed_url: str) -> list[dict[str, str]]:
    """Coleta e normaliza todas as entradas disponiveis em um feed."""
    LOGGER.info("Lendo feed: %s", feed_url)
    feed = feedparser.parse(
        feed_url,
        request_headers={"User-Agent": "insurance-intelligence-letter/1.0"},
    )
    if feed.bozo:
        LOGGER.warning("Feed retornou alerta de parsing: %s", feed.bozo_exception)
    if not feed.entries:
        LOGGER.warning("Nenhuma entrada encontrada em %s", feed_url)
        return []

    source = clean_html(feed.feed.get("title")) or feed_url
    items: list[dict[str, str]] = []
    for entry in feed.entries:
        title = clean_html(entry.get("title"))
        link = str(entry.get("link", "")).strip()
        if not title or not link:
            LOGGER.debug("Entrada ignorada por falta de titulo ou link")
            continue

        published_at = parse_entry_date(entry)
        summary = clean_html(
            entry.get("summary")
            or entry.get("description")
            or entry.get("content", [{}])[0].get("value", "")
        )
        items.append(
            {
                "title": title,
                "link": link,
                "date": published_at.isoformat(),
                "summary": summary,
                "source": source,
            }
        )
    return items


def deduplicate(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Remove duplicatas por link, preservando a primeira ocorrencia."""
    unique: dict[str, dict[str, str]] = {}
    for item in items:
        unique.setdefault(item["link"], item)
    return list(unique.values())


def main() -> None:
    """Executa a coleta, ordenacao e persistencia."""
    all_items: list[dict[str, str]] = []
    for feed_url in RSS_FEEDS:
        try:
            all_items.extend(collect_feed(feed_url))
        except Exception:  # Mantem os outros feeds funcionando.
            LOGGER.exception("Falha inesperada ao processar %s", feed_url)

    items = deduplicate(all_items)
    items.sort(key=lambda item: item["date"], reverse=True)
    selected = items[:NEWS_LIMIT]
    if not selected:
        raise RuntimeError("Nenhuma noticia foi coletada. Verifique os feeds e a rede.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(selected, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    LOGGER.info("%d noticias salvas em %s", len(selected), OUTPUT_FILE)


if __name__ == "__main__":
    main()
