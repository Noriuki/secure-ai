# Backend

```bash
# Postgres (na raiz do monorepo)
docker compose up -d db

uv sync --extra dev
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
uv run pytest
```

Migrations:

```bash
uv run alembic revision --autogenerate -m "descricao"
uv run alembic upgrade head
```

Arquitetura por feature: cada módulo em `app/modules/<nome>` contém router, service, repository, models e schemas.
