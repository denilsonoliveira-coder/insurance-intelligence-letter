"""Gera a newsletter executiva em HTML usando a OpenAI API."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from openai import OpenAI

from config import NEWSLETTER_NAME, OPENAI_MODEL

BASE_DIR = Path(__file__).resolve().parents[1]
NEWS_FILE = BASE_DIR / "output" / "news.json"
LETTER_FILE = BASE_DIR / "output" / "letter.html"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)

STRATEGIC_PROMPT = r"""
Você é um consultor estratégico especialista no mercado segurador brasileiro.

Seu público é um Product Manager responsável por produtos de seguros digitais,
embedded insurance e distribuição de seguros em concessionárias de energia.

Analise todas as notícias fornecidas. Não se limite a resumir notícias.
Para cada notícia identifique: o que aconteceu; por que importa; possível impacto
para seguradoras; canais digitais; embedded insurance; utilities e concessionárias.
Classifique cada item como: Ação Imediata, Oportunidade, Benchmark ou Contexto.

Estruture a resposta como newsletter executiva semanal e inclua obrigatoriamente:
1. Insurance Intelligence Letter
2. Resumo Executivo
3. Radar Regulatório: SUSEP, CNSP, BACEN, LGPD e Open Insurance
4. Movimentos dos Concorrentes: Porto, Tokio Marine, Allianz, SulAmérica,
   Bradesco Seguros, Pier, Justos e Kakau
5. Tendências Emergentes
6. Oportunidades para o Hub de Seguros
7. Top 5 Oportunidades
8. Top 5 Riscos
9. Top 5 Tendências
10. Ideias de Novos Produtos, com pelo menos 3 ideias
11. Ideias de Experimentos, com pelo menos 3 ideias
12. O que merece ação agora
13. O que merece discovery
14. O que merece benchmark
15. O que pode ser ignorado
16. O que eu faria se fosse o PM do produto, com recomendações para a próxima semana

Regras de qualidade:
- Use apenas os fatos presentes nas notícias recebidas.
- Não invente fatos, números, regulações ou movimentos de concorrentes.
- Quando não houver evidência para uma seção, informe que não houve sinal relevante
  nos feeds daquela semana.
- Diferencie fato, inferência e recomendação.
- Inclua links clicáveis para as fontes em cada análise relevante.
- Priorize objetividade, impacto e decisões práticas.
- Escreva em português do Brasil.

Retorne um documento HTML completo, moderno, responsivo e compatível com clientes
de e-mail. Use CSS inline ou em uma tag <style>, largura máxima de 760px, fundo
claro, tipografia segura, cards discretos e cores corporativas em azul. Não use
JavaScript, Markdown, imagens externas ou recursos remotos. Retorne somente HTML.
""".strip()


def load_news() -> list[dict[str, Any]]:
    """Carrega e valida o arquivo de notícias."""
    if not NEWS_FILE.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {NEWS_FILE}")
    data = json.loads(NEWS_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("news.json deve conter uma lista não vazia.")
    return data


def build_input(news: list[dict[str, Any]]) -> str:
    """Monta o contexto estruturado enviado ao modelo."""
    today = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")
    payload = json.dumps(news, ensure_ascii=False, indent=2)
    return f"Data de referência: {today}\n\nNOTÍCIAS EM JSON:\n{payload}"


def normalize_html(raw: str) -> str:
    """Remove cercas Markdown e garante um documento HTML completo."""
    cleaned = re.sub(r"^\s*```(?:html)?\s*|\s*```\s*$", "", raw.strip(), flags=re.I)
    if "<html" not in cleaned.lower():
        cleaned = (
            '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f"<title>{escape(NEWSLETTER_NAME)}</title></head><body>{cleaned}</body></html>"
        )
    return cleaned


def main() -> None:
    """Solicita a análise à OpenAI e grava o HTML resultante."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError("A variável OPENAI_API_KEY não foi definida.")

    news = load_news()
    LOGGER.info("Gerando newsletter com %d notícias e modelo %s", len(news), OPENAI_MODEL)
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=STRATEGIC_PROMPT,
        input=build_input(news),
        max_output_tokens=16000,
    )
    html_text = response.output_text
    if not html_text or not html_text.strip():
        raise RuntimeError("A OpenAI API retornou uma resposta vazia.")

    LETTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    LETTER_FILE.write_text(normalize_html(html_text), encoding="utf-8")
    LOGGER.info("Newsletter salva em %s", LETTER_FILE)


if __name__ == "__main__":
    main()
