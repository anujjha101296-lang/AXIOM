# Multi-stage Dockerfile for AXIOM API Gateway
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

# Keep the container dependency set aligned with pyproject.toml.
RUN pip install --upgrade pip && \
    pip install --prefix=/install \
    fastapi \
    'uvicorn[standard]' \
    pydantic \
    pydantic-settings \
    networkx \
    sympy \
    pylatexenc \
    requests \
    z3-solver \
    anyio \
    pypdf \
    python-multipart \
    'passlib[bcrypt]' \
    'python-jose[cryptography]' \
    email-validator \
    bcrypt \
    sqlalchemy \
    alembic \
    greenlet \
    aiosqlite \
    google-generativeai \
    openai \
    openai-agents

FROM python:3.11-slim AS runtime

RUN groupadd -r axiom && useradd -r -g axiom -d /app -s /sbin/nologin axiom

WORKDIR /app
COPY --from=builder /install /usr/local
COPY axiom/ ./axiom/
COPY pyproject.toml ./

RUN mkdir -p /tmp/axiom_proofs && chown axiom:axiom /tmp/axiom_proofs

USER axiom

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    LOG_FORMAT=json \
    LOG_LEVEL=INFO

# Render supplies PORT. Keep 10000 as the Docker fallback for standard Render web services.
EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD-SHELL python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\", \"10000\")}/health')" || exit 1

CMD ["sh", "-c", "exec python -m uvicorn axiom.services.api_gateway.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers ${WEB_CONCURRENCY:-2}"]
