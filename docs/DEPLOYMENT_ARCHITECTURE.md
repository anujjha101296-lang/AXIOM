# Deployment Architecture

## Frontend
- **Framework**: Next.js
- **Deployment Platform**: Vercel
- **Configuration**: Vercel builds the `ui/` directory.

## Backend
- **Framework**: FastAPI
- **Deployment Platform**: External service (e.g., Fly.io, Render, AWS ECS)
- **Configuration**: DO NOT deploy on Vercel. FastAPI runs indefinite research workers (Z3 SMT solver subprocesses and multi-step LLM loops) that exceed Vercel's serverless timeout limits.

## Database
- **Primary Data**: PostgreSQL (External persistent infrastructure)
- **Local Dev**: SQLite (`axiom.db`)

## Workers
- **Type**: Long-running research tasks
- **Deployment Platform**: External service (same as Backend or dedicated Celery/RQ instances).

## Queue
- **Type**: Redis / In-memory
- **Deployment Platform**: External service.

## Vector Store
- **Type**: Local/Ephemeral (SQLite) -> Migrate to pgvector for production.
- **Deployment Platform**: External service.

## Object Storage
- **Type**: AWS S3 / Cloudflare R2
- **Deployment Platform**: External service.

## LLM Providers
- **Providers**: OpenAI, Google Gemini
- **Deployment Platform**: External API.

## Search Providers
- **Providers**: Web search tools
- **Deployment Platform**: External API.

## Formal Verification
- **Providers**: Z3 Theorem Prover, Lean 4
- **Deployment Platform**: Packaged within the Backend Docker container (External service).
