# API para Power BI

Esta API conecta ao banco PostgreSQL e expõe as tabelas em endpoints REST para o Power BI consumir.

## Estrutura

- `app/config.py`: leitura das variáveis do `.env`
- `app/database.py`: conexão com o banco e consultas
- `app/main.py`: endpoints da API

## Variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e ajuste os valores:

```bash
cp .env.example .env
```

Exemplo:

```env
DB_HOST=143.95.171.53
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=sua_senha
TABLE_NAME=nome_da_tabela
API_KEY=
```

## Rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

A API estará disponível em:

- http://localhost:8000
- http://localhost:8000/docs

## Endpoints

### Health check

```http
GET /health
```

### Listar tabelas

```http
GET /tables
```

### Consultar uma tabela

```http
GET /api/data?table_name=nome_da_tabela&limit=1000&offset=0
```

### Exemplo no Power BI

```powerquery
let
    url = "http://localhost:8000/api/data?table_name=nome_da_tabela&limit=1000",
    Source = Json.Document(Web.Contents(url)),
    Rows = Source[rows]
in
    Rows
```

## Executar com Docker

```bash
docker compose up --build
```

A API ficará disponível em http://localhost:8000
