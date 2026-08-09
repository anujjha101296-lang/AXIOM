# Multi-stage Dockerfile for AXIOM API Gateway
# Stage 1: Builder — installs package + dependencies
# Stage 2: Runtime — minimal production image

FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY axiom/ ./axiom/

RUN pip install --upgrade pip && \
    pip install --prefix=/install .

FROM python:3.11-slim AS runtime

RUN groupadd -r axiom && useradd -r -g axiom -d /app -s /sbin/nologin axiom

WORKDIR /app

COPY --from=builder /install /usr/local
COPY axiom/ ./axiom/
COPY pyproject.toml ./

RUN mkdir -p /data /tmp/axiom_proofs /app/research_uploads && \
    chown -R axiom:axiom /data /tmp/axiom_proofs /app/research_uploads /app

USER axiom

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    LOG_FORMAT=json \
    LOG_LEVEL=INFO \
    DB_PATH=/data/axiom.db \
    RESEARCH_UPLOAD_DIR=/app/research_uploads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "uvicorn", "axiom.services.api_gateway.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
