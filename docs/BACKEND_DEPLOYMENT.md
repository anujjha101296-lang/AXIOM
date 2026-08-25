# AXIOM Backend Deployment Guide

The AXIOM backend requires a persistent, long-lived container environment to safely execute multi-agent research loops, formal solver subprocesses (Z3), and stateful database interactions. It MUST NOT be deployed on Vercel.

## Recommended Platforms
1. **Render (Web Service)** - Preferred for ease of configuration.
2. **Fly.io** - Preferred for distributed geographic edges and simple PostgreSQL clusters.
3. **AWS ECS / Fargate** - Preferred for enterprise scalability.

## Configuration Details
- **Service Type**: Docker Container Web Service
- **Region**: Any (Match database region for latency, e.g., `us-east-1` or `sfo`)
- **Container**: `Dockerfile` in the root repository.
- **Port**: `8000` (Exposed natively by Uvicorn)
- **Health Check Path**: `/health` (or `/ready` for database-coupled health checks)
- **Database**: PostgreSQL (e.g., Supabase or Render Managed PostgreSQL). 

## Required Environment Variables
| Variable | Description |
| :--- | :--- |
| `ENVIRONMENT` | Must be strictly `production`. |
| `DATABASE_URL` | e.g., `postgresql+asyncpg://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | Strongly randomized 256-bit string for signing auth tokens. |
| `OPENAI_API_KEY` | Required if `DEFAULT_MODEL` is an OpenAI model. |
| `GEMINI_API_KEY` | Required if `DEFAULT_MODEL` is a Gemini model. |

## Scaling & Worker Architecture
For production deployments exceeding MVP scale, the indefinite reasoning tasks (e.g., `ResearchPlanner`) should be decoupled from the synchronous HTTP request via a message queue (e.g., Celery/Redis). Currently, the HTTP request loop handles bounded research; this implies a slightly elevated timeout configuration is required on the ingress load balancer (e.g., `300s` instead of the default `60s`).

## Deployment Procedure

1. **Database Allocation**: Provision a managed PostgreSQL database (e.g., Supabase or Render PostgreSQL).
2. **Secret Injection**: Add `DATABASE_URL`, `OPENAI_API_KEY`, and `JWT_SECRET_KEY` into the deployment platform's Secret Manager.
3. **Container Build**: Point the deployment service to the `Dockerfile` at the repository root.
4. **Health Verification**: Monitor the build logs. Verify that `GET /health` and `GET /health/ready` return 200 before routing live traffic.
5. **Frontend Bind**: Copy the resulting HTTPS URL (e.g., `https://axiom-api.onrender.com`) and set it as `NEXT_PUBLIC_API_URL` in the Vercel Frontend dashboard.

## Rollback Procedure
If a deployment fails, use the provider dashboard to trigger a "Rollback" to the previously healthy image hash. Do not modify the database schema without a forward-only Alembic migration.
