# Insurance Intelligence Letter

Automação gratuita para coletar notícias do mercado de seguros brasileiro via RSS, gerar uma análise executiva semanal com a Gemini API e enviar a newsletter em HTML por e-mail usando GitHub Actions.

## 1. Objetivo

O projeto entrega, toda segunda-feira às 08:00 no horário de Brasília, uma newsletter voltada a Product Managers de seguros digitais, embedded insurance e distribuição por utilities. O fluxo coleta até 20 notícias, pede ao Gemini uma análise estratégica e envia o resultado via SMTP.

> A automação usa serviços com opções gratuitas, mas limites e condições dos provedores podem mudar. Consulte as páginas de preços e cotas antes de ampliar o volume.

## 2. Arquitetura

```text
RSS feeds
   |
   v
scripts/news_collector.py --> output/news.json
   |
   v
scripts/generate_letter.py + Gemini API --> output/letter.html
   |
   v
scripts/send_email.py + SMTP --> Caixa de entrada
```

Estrutura:

```text
insurance-intelligence-letter/
├── .github/workflows/insurance-letter.yml
├── scripts/
│   ├── config.py
│   ├── news_collector.py
│   ├── generate_letter.py
│   └── send_email.py
├── output/
│   ├── news.json
│   └── letter.html
├── requirements.txt
├── .gitignore
└── README.md
```

## 3. Como criar a API Key do Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/apikey).
2. Entre com sua conta Google.
3. Selecione **Create API key** e escolha ou crie um projeto.
4. Copie a chave e guarde-a em um gerenciador de senhas.
5. No GitHub, cadastre-a como secret com o nome `GEMINI_API_KEY`.

Nunca coloque a chave diretamente no código, em commits, logs ou no arquivo `.env` versionado.

O modelo padrão é `gemini-2.5-flash`. Para trocar, defina a variável opcional `GEMINI_MODEL` no ambiente ou no workflow.

## 4. Como configurar SMTP Gmail

1. Ative a verificação em duas etapas na Conta Google.
2. Crie uma **Senha de app** para esta automação.
3. Use o endereço completo do Gmail em `EMAIL_USER`.
4. Use a senha de app de 16 caracteres em `EMAIL_PASSWORD`, não a senha comum.
5. O projeto detecta Gmail e usa `smtp.gmail.com`, porta `587`, com STARTTLS.

Algumas contas corporativas podem bloquear senhas de app. Nesse caso, o administrador precisa liberar uma alternativa adequada, como relay SMTP ou OAuth. O projeto atual implementa autenticação SMTP por usuário e senha de app.

## 5. Como configurar SMTP Outlook

Para contas pessoais Outlook.com, Hotmail, Live ou MSN, o projeto seleciona `smtp-mail.outlook.com`, porta `587`, com STARTTLS. Para domínios corporativos Microsoft 365, utiliza `smtp.office365.com` por padrão.

A Microsoft prioriza OAuth2/Modern Auth e pode bloquear autenticação básica SMTP. Portanto:

1. Confirme com o administrador se **Authenticated SMTP** está habilitado para a caixa.
2. Se a conta aceitar senha de app, use-a em `EMAIL_PASSWORD`.
3. Se o tenant exigir somente OAuth2, este projeto precisará ser ampliado com Microsoft Graph ou OAuth2 para SMTP. Usuário e senha simples não serão suficientes.
4. Para outro servidor, cadastre `SMTP_HOST`, `SMTP_PORT` e, opcionalmente, `SMTP_STARTTLS`.

## 6. Como cadastrar Secrets no GitHub

No repositório:

1. Acesse **Settings**.
2. Abra **Secrets and variables** > **Actions**.
3. Clique em **New repository secret**.
4. Cadastre:
   - `GEMINI_API_KEY`: chave da Gemini API.
   - `EMAIL_USER`: conta remetente.
   - `EMAIL_PASSWORD`: senha de app ou credencial SMTP permitida.
   - `EMAIL_TO`: destinatários, separados por vírgula ou ponto e vírgula.
5. Salve cada secret.

Secrets são mascarados nos logs, mas evite imprimi-los no código.

## 7. Como executar localmente

Pré-requisitos: Python 3.11 e Git.

```bash
git clone URL_DO_SEU_REPOSITORIO
cd insurance-intelligence-letter
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Defina as variáveis no terminal Linux/macOS:

```bash
export GEMINI_API_KEY="sua-chave"
export EMAIL_USER="seu-email@gmail.com"
export EMAIL_PASSWORD="sua-senha-de-app"
export EMAIL_TO="destinatario@empresa.com"
```

No PowerShell:

```powershell
$env:GEMINI_API_KEY="sua-chave"
$env:EMAIL_USER="seu-email@gmail.com"
$env:EMAIL_PASSWORD="sua-senha-de-app"
$env:EMAIL_TO="destinatario@empresa.com"
```

Execute em sequência:

```bash
python scripts/news_collector.py
python scripts/generate_letter.py
python scripts/send_email.py
```

## 8. Como testar manualmente

1. Faça push do projeto para a branch padrão.
2. Abra a aba **Actions**.
3. Selecione **Insurance Intelligence Letter**.
4. Clique em **Run workflow**.
5. Escolha a branch e clique novamente em **Run workflow**.
6. Aguarde as etapas de coleta, geração e envio.

Para testar sem enviar e-mail, execute somente os dois primeiros scripts localmente e abra `output/letter.html` no navegador.

## 9. Como acompanhar logs do GitHub Actions

1. Abra **Actions** no repositório.
2. Clique na execução desejada.
3. Abra o job **Gerar e enviar newsletter**.
4. Expanda cada etapa para consultar os logs.
5. Ao final, baixe o artifact da execução para inspecionar `news.json` e `letter.html`.

O workflow publica os arquivos de saída mesmo quando uma etapa falha, desde que tenham sido criados. A retenção configurada é de 14 dias.

## 10. Como adicionar novos RSS

Edite `scripts/config.py` e acrescente a URL:

```python
RSS_FEEDS = [
    "https://www.sonhoseguro.com.br/feed/",
    "https://cqcs.com.br/feed/",
    "https://exemplo.com.br/feed/",
]
```

O feed deve ser RSS ou Atom válido. O coletor remove duplicatas por link e ordena por data. Para alterar o limite, modifique `NEWS_LIMIT` ou defina a variável de ambiente de mesmo nome.

## 11. Solução de problemas comuns

### `GEMINI_API_KEY nao foi definida`
Cadastre o secret com o nome exato ou exporte a variável localmente.

### Modelo Gemini não encontrado ou sem cota
Verifique a disponibilidade do modelo para sua conta e região. Defina `GEMINI_MODEL` com um modelo habilitado e confira as cotas no Google AI Studio.

### `SMTPAuthenticationError`
Use senha de app, confirme usuário e senha, verifique se SMTP AUTH está habilitado e se o provedor permite esse método. No Outlook corporativo, o tenant pode exigir OAuth2.

### Gmail bloqueou o login
Ative verificação em duas etapas e gere uma senha de app. Não utilize a senha normal da conta.

### Feed sem notícias
Abra a URL do feed no navegador, confira se responde e se é RSS/Atom válido. O job falha apenas se nenhum feed produzir notícias utilizáveis.

### Newsletter com informação não sustentada
O prompt orienta o modelo a usar apenas os feeds e declarar ausência de sinais. Mesmo assim, IA generativa pode errar. Revise o conteúdo antes de decisões regulatórias, jurídicas ou financeiras.

### Execução não iniciou exatamente às 08:00
Agendamentos do GitHub Actions podem sofrer atraso. O cron usa `0 11 * * 1`, pois o agendador trabalha em UTC e 11:00 UTC corresponde a 08:00 em Brasília.

### Arquivos de output não aparecem no Git
Eles são placeholders no repositório, mas novas versões geradas são ignoradas pelo `.gitignore`. Nas execuções, ficam disponíveis como artifacts.

## Segurança e evolução futura

- Não versione credenciais.
- Restrinja acesso ao repositório e aos secrets.
- Revise dependências periodicamente.
- Para Outlook com Modern Auth, considere Microsoft Graph.
- Para maior cobertura, adicione fontes oficiais de SUSEP, CNSP, BACEN e ANPD.
- Para evitar repetição semanal, persista histórico em uma branch, release, banco gratuito ou storage externo.
- Para produção crítica, adicione testes, validação de links, observabilidade e aprovação humana antes do envio.
