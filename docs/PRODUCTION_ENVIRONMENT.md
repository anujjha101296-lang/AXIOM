# Production Environment Configuration

This document defines the strict environmental contract required for the AXIOM FastAPI backend to operate in production. 

> **SECURITY RULE**: Never commit values to version control. Set these explicitly in your provider (e.g., Render Dashboard, Fly.io secrets, AWS Parameter Store).

## Required Variables

| Variable | Purpose | Where Configured | Secret? |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | MUST be set to `production` to disable all deterministic mock fallbacks. | Provider Dashboard | No |
| `DATABASE_URL` | Connection string for a persistent PostgreSQL cluster (e.g., `postgresql+asyncpg://user:pass@host/db`). | Provider Dashboard | Yes |
| `JWT_SECRET_KEY` | 256-bit cryptographic signing key for authenticating user tokens. | Provider Dashboard | Yes |
| `OPENAI_API_KEY` | Provides live connectivity for the `OpenAILLMProvider` and embeddings. | Provider Dashboard | Yes |

## Optional Variables

| Variable | Purpose | Where Configured | Secret? |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Required only if `DEFAULT_MODEL` is set to a Gemini model. | Provider Dashboard | Yes |
| `DEFAULT_MODEL` | Changes the upstream model target (e.g., `gpt-4o`). Default: `gpt-4o-mini`. | Provider Dashboard | No |
| `CORS_ORIGINS` | Commma-separated list of allowed frontend domains (e.g., `https://axiom.vercel.app`). Defaults to strict lockdown. | Provider Dashboard | No |

If any `Required` variable is missing when `ENVIRONMENT=production`, the application will intentionally throw a 500 `ConfigurationError` and refuse to boot.
