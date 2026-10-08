"""Envia a newsletter HTML por SMTP."""
from __future__ import annotations
import logging, os, smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo
from config import EMAIL_SUBJECT_PREFIX, NEWSLETTER_NAME, get_smtp_settings
BASE_DIR=Path(__file__).resolve().parents[1]
LETTER_FILE=BASE_DIR/'output'/'letter.html'
logging.basicConfig(level=logging.INFO,format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
LOGGER=logging.getLogger(__name__)

def require_env(name:str)->str:
    value=os.getenv(name,'').strip()
    if not value: raise EnvironmentError(f'A variável {name} não foi definida.')
    return value

def parse_recipients(raw:str)->list[str]:
    recipients=[x.strip() for x in raw.replace(';',',').split(',') if x.strip()]
    if not recipients: raise ValueError('EMAIL_TO não contém destinatários válidos.')
    return recipients

def main()->None:
    sender=require_env('EMAIL_USER'); password=require_env('EMAIL_PASSWORD')
    recipients=parse_recipients(require_env('EMAIL_TO'))
    if not LETTER_FILE.exists(): raise FileNotFoundError(f'Newsletter não encontrada: {LETTER_FILE}')
    html=LETTER_FILE.read_text(encoding='utf-8')
    date=datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y')
    message=EmailMessage(); message['Subject']=f'{EMAIL_SUBJECT_PREFIX} - {date}'
    message['From']=f'{NEWSLETTER_NAME} <{sender}>'; message['To']=', '.join(recipients)
    message.set_content('Abra este e-mail em um cliente compatível com HTML.')
    message.add_alternative(html,subtype='html')
    settings=get_smtp_settings(sender)
    with smtplib.SMTP(settings.host,settings.port,timeout=30) as smtp:
        smtp.ehlo()
        if settings.use_starttls: smtp.starttls(); smtp.ehlo()
        smtp.login(sender,password); smtp.send_message(message)
    LOGGER.info('Newsletter enviada para %d destinatário(s).',len(recipients))
if __name__=='__main__': main()
