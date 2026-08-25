# Deployment Architecture

## Frontend
- **Framework**: Next.js
- **Deployment Platform**: Vercel
- **CRITICAL VERCEL CONFIGURATION**: You MUST set the Vercel **Root Directory** to `ui` in the Vercel Dashboard (Settings > General > Root Directory). Do NOT use a `vercel.json` file in the repository root to configure this, as Vercel's framework detection will crash looking for `package.json` at the root.

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
