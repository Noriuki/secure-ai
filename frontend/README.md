# Frontend

```bash
npm install
cp .env.example .env
npm run dev
```

Estrutura por feature em `src/features/<nome>`: `types` → `api` → `hooks` → `components`.

Configure `VITE_API_BASE_URL` no `.env` (ex.: `http://localhost:8000/api/v1`). O backend libera CORS para a origem do Vite.
