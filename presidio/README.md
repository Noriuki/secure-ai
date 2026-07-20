# Presidio Analyzer (pt)

Texto → `POST /analyze` (spaCy `pt` + CPF/CNPJ/…).  
Anonimização (`{{PII_TYPE_N}}`) fica no app FastAPI.

```bash
docker compose up -d --build presidio-analyzer
```

Health: http://localhost:5003/health

```bash
curl -s http://localhost:5003/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"CPF 529.982.247-25 e email maria@demo.com","language":"pt"}'
```
