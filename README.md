# Insurance Intelligence Letter com OpenAI

Automação semanal que coleta notícias do mercado de seguros por RSS, gera uma newsletter executiva em HTML com a OpenAI API e envia por SMTP.

## Secrets obrigatórios

Cadastre em `Settings > Secrets and variables > Actions`:

- `OPENAI_API_KEY`: chave da OpenAI API.
- `EMAIL_USER`: endereço remetente.
- `EMAIL_PASSWORD`: credencial SMTP ou senha de aplicativo.
- `EMAIL_TO`: um ou mais destinatários, separados por vírgula.

Remova o antigo secret `GEMINI_API_KEY`, pois ele não é mais utilizado.

## Modelo

O modelo padrão é `gpt-5-mini`. Para usar outro modelo disponível em sua conta, crie uma variável de ambiente ou ajuste o workflow com:

```text
OPENAI_MODEL=nome-do-modelo
```

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sua-chave"
export EMAIL_USER="seu-email@outlook.com"
export EMAIL_PASSWORD="sua-credencial-smtp"
export EMAIL_TO="destinatario@exemplo.com"
python scripts/news_collector.py
python scripts/generate_letter.py
python scripts/send_email.py
```

No Windows PowerShell, use `$env:NOME="valor"`.

## Execução no GitHub

O workflow roda toda segunda-feira às 11:00 UTC, equivalente a 08:00 em Brasília, e também pode ser executado manualmente em `Actions > Insurance Intelligence Letter > Run workflow`.

## Atenção a custos

A API da OpenAI é separada de assinaturas do ChatGPT e pode exigir faturamento ou créditos de API. Monitore o uso e defina limites de gasto na plataforma da OpenAI.
