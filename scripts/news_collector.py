"""Coleta notícias de feeds RSS e salva as mais recentes em JSON."""
from __future__ import annotations
import json, logging, re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
import feedparser
from bs4 import BeautifulSoup
from config import NEWS_LIMIT, RSS_FEEDS
BASE_DIR=Path(__file__).resolve().parents[1]
OUTPUT_FILE=BASE_DIR/'output'/'news.json'
logging.basicConfig(level=logging.INFO,format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
LOGGER=logging.getLogger(__name__)

def clean_html(value: str|None)->str:
    if not value: return ''
    return re.sub(r'\s+',' ',BeautifulSoup(value,'html.parser').get_text(' ',strip=True)).strip()

def parse_entry_date(entry: Any)->datetime:
    for field in ('published_parsed','updated_parsed','created_parsed'):
        value=entry.get(field)
        if value: return datetime(*value[:6],tzinfo=timezone.utc)
    for field in ('published','updated','created'):
        value=entry.get(field)
        if value:
            try:
                parsed=parsedate_to_datetime(value)
                if parsed.tzinfo is None: parsed=parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
            except (TypeError,ValueError,OverflowError): pass
    return datetime.now(timezone.utc)

def collect_feed(url: str)->list[dict[str,str]]:
    LOGGER.info('Lendo feed: %s',url)
    feed=feedparser.parse(url,request_headers={'User-Agent':'insurance-intelligence-letter/1.0'})
    if feed.bozo: LOGGER.warning('Alerta ao interpretar feed: %s',feed.bozo_exception)
    source=clean_html(feed.feed.get('title')) or url
    result=[]
    for entry in feed.entries:
        title=clean_html(entry.get('title')); link=str(entry.get('link','')).strip()
        if not title or not link: continue
        content=entry.get('content') or [{}]
        summary=clean_html(entry.get('summary') or entry.get('description') or content[0].get('value',''))
        result.append({'title':title,'link':link,'date':parse_entry_date(entry).isoformat(),'summary':summary,'source':source})
    return result

def main()->None:
    items=[]
    for url in RSS_FEEDS:
        try: items.extend(collect_feed(url))
        except Exception: LOGGER.exception('Falha ao processar %s',url)
    unique={item['link']:item for item in items}
    selected=sorted(unique.values(),key=lambda x:x['date'],reverse=True)[:NEWS_LIMIT]
    if not selected: raise RuntimeError('Nenhuma notícia foi coletada.')
    OUTPUT_FILE.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
    LOGGER.info('%d notícias salvas em %s',len(selected),OUTPUT_FILE)
if __name__=='__main__': main()
