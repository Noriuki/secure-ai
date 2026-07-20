# Secure AI

Boilerplate clean code com **FastAPI** (módulos por feature) e **React + Vite + TypeScript**.

## Estrutura

```text
secure-ai/
├── docker-compose.yml       # Postgres + Presidio Analyzer (pt)
├── presidio/                # Analyzer custom (CPF/CNPJ, spaCy pt)
├── docs/                    # Arquitetura resumida
├── infra/                   # Esqueleto Terraform (dev stub)
├── fixtures/                # Documentos de demonstração
├── backend/                 # API FastAPI
│   ├── alembic/             # migrations
│   └── app/
│       ├── core/            # config, db, exceptions, security/vault
│       ├── integrations/    # S3, Bedrock, Presidio, PDF
│       ├── modules/         # workspaces, documents, conversations, audit
│       ├── api.py
│       └── main.py
└── frontend/                # React Vite TS
```

## Backend

```bash
# Na raiz: Postgres + Presidio Analyzer (pt)
docker compose up -d --build db presidio-analyzer

cd backend
uv sync --extra dev
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health
- Presidio: http://127.0.0.1:5003/health
- Stack: **Postgres** + **Presidio (pt)** + **SQLAlchemy 2** + **Alembic**
- PII: texto → `/analyze` → tokens `{{PII_...}}` + vault

Testes:

```bash
uv run pytest
```

Migrations:

```bash
uv run alembic revision --autogenerate -m "descricao"
uv run alembic upgrade head
```

### Como adicionar uma feature

1. Crie `app/modules/<feature>/` com `schemas.py`, `models.py`, `repository.py`, `service.py`, `router.py`
2. Importe o model em `alembic/env.py` (ou num `app/models` agregador) e gere a migration
3. Inclua o router em `app/api.py`
4. Mantenha a regra: **router fino → service com regras → repository (SQLAlchemy Session)**

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: http://localhost:5173

O front chama a API em `VITE_API_BASE_URL` (ex.: `http://localhost:8000/api/v1`). O FastAPI libera CORS para `localhost:5173`.

### Como adicionar uma feature

1. Crie `src/features/<feature>/` com `types.ts`, `api.ts`, `hooks/`, `components/`
2. Use o client em `src/shared/api/client.ts`
3. Monte a tela em `src/app/App.tsx` (ou um router depois)

## Scripts úteis

| Onde       | Comando                          |
|------------|----------------------------------|
| raiz       | `docker compose up -d db presidio-analyzer` |
| infra      | `./scripts/init.sh dev`          |
| infra      | `./scripts/deploy.sh dev`        |
| backend    | `uv run alembic upgrade head`    |
| backend    | `uv run uvicorn app.main:app --reload` |
| backend    | `uv run pytest`                  |
| frontend   | `npm run dev`                    |
| frontend   | `npm run build`                  |

Infra AWS (Terraform): ver [`infra/README.md`](infra/README.md).

