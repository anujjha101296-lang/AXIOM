# AXIOM — Deployment Architecture

## Overview

AXIOM is a split-stack application:

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Next.js | Deployed to Vercel |
| Backend API | FastAPI + Uvicorn | Deployed as Docker container |
| Database | SQLite (dev) / PostgreSQL (prod) | Persistent volume required |
| Vector Storage | Python KNN over SQLite (dev) / pgvector (prod) | |
| LLM Provider | Google Gemini / OpenAI | External API |
| Embedding Provider | OpenAI / Gemini / Mock (test) | External API |

---

## Frontend (Vercel)

```bash
cd ui
npm install
npm run build
# Deployed automatically via Vercel Git integration
```

**Important:** Vercel has no persistent filesystem. Do NOT store uploaded documents or vector databases on Vercel. All file storage must use the backend API.

---

## Backend (Docker)

### Build

```bash
docker build -t axiom-backend .
```

### Run locally

```bash
docker run -p 8000:8000 \
  -e JWT_SECRET_KEY=your-secret \
  -e GEMINI_API_KEY=your-gemini-key \
  -e EMBEDDING_PROVIDER=gemini \
  -e DATABASE_URL=sqlite+aiosqlite:///./axiom.db \
  axiom-backend
```

### Deploy to Cloud Run / Fly.io

```bash
# Cloud Run
gcloud run deploy axiom-backend \
  --image axiom-backend \
  --set-env-vars JWT_SECRET_KEY=...,GEMINI_API_KEY=...,EMBEDDING_PROVIDER=gemini

# Fly.io
fly deploy
```

---

## Database

### Development (SQLite)

```bash
# Apply migrations
.venv312/bin/alembic upgrade head

# DATABASE_URL (in .env)
DATABASE_URL=sqlite+aiosqlite:///./axiom.db
```

### Production (PostgreSQL)

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/axiom

# Install pgvector extension for semantic search at scale:
# CREATE EXTENSION IF NOT EXISTS vector;
```

> **Note:** The current vector store uses Python-side cosine similarity over SQLite-stored JSON arrays. This is suitable for corpora up to ~10k chunks. For production scale, migrate to pgvector with an HNSW or IVFFlat index.

---

## Vector Storage

| Environment | Backend | Limit |
|-------------|---------|-------|
| Development/Test | Python KNN over SQLite JSON arrays | ~10k chunks |
| Production | PostgreSQL + pgvector (upgrade path) | Millions of chunks |

---

## Required Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | Yes | Random 32+ char secret for JWT signing |
| `DATABASE_URL` | Yes | SQLAlchemy connection URL |
| `EMBEDDING_PROVIDER` | Yes | `openai`, `gemini`, or `test` |
| `OPENAI_API_KEY` | If provider=openai | OpenAI API key |
| `GEMINI_API_KEY` | If provider=gemini | Google Gemini API key |
| `DEFAULT_MODEL` | No | LLM model name (e.g. `gemini-1.5-pro`) |
| `EMBEDDING_MODEL` | No | Embedding model name override |
| `ENVIRONMENT` | No | `test`/`development`/`production` |

---

## Database Migrations

```bash
# Apply all migrations
.venv312/bin/alembic upgrade head

# Create new migration after model changes
.venv312/bin/alembic revision --autogenerate -m "description"
```

---

## File Storage

**Development:** Files are uploaded in-memory and processed immediately. No disk persistence of raw files.

**Production:** For durable file storage, integrate with:
- Google Cloud Storage (GCS)
- AWS S3
- Cloudflare R2

---

## Known Limitations

1. **No persistent raw file storage**: Uploaded files are processed in-memory. Raw PDFs are not stored on disk.
2. **Vector store scalability**: Current SQLite KNN is O(n) per query. Use pgvector for production.
3. **Vercel frontend**: No server-side persistent state. All data flows through the backend API.
4. **Async SQLAlchemy on Python 3.13**: Requires `greenlet` and `aiosqlite` installed.
5. **Embedding cost**: Production embedding calls are billed per token. Cache strategy not yet implemented.
6. **Single-process deployment**: Current architecture does not support multi-worker embedding without a shared DB.

---

## Security Checklist

- [ ] `JWT_SECRET_KEY` is a strong random value (not the default)
- [ ] `.env` is in `.gitignore` and never committed
- [ ] API keys are environment variables, never hardcoded
- [ ] Database has connection encryption in production (`sslmode=require`)
- [ ] CORS origins are restricted to known frontends in production
- [ ] File upload size limits are enforced
- [ ] Document text is treated as DATA, never as trusted instructions
