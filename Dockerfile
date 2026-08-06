# Multi-stage Dockerfile for AXIOM API Gateway
# Stage 1: Builder — installs all dependencies
# Stage 2: Runtime — minimal production image

# ────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# ────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency spec first for cache efficiency
COPY pyproject.toml ./

# Install all Python dependencies into a prefix directory
RUN pip install --upgrade pip && \
    pip install --prefix=/install \
    fastapi \
    uvicorn[standard] \
    pydantic \
    pydantic-settings \
    networkx \
    sympy \
    pylatexenc \
    requests \
    z3-solver \
    anyio \
    pypdf \
    python-multipart

# ────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime
# ────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Non-root user for security
RUN groupadd -r axiom && useradd -r -g axiom -d /app -s /sbin/nologin axiom

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY axiom/ ./axiom/
COPY pyproject.toml ./

# Create lean output directory
RUN mkdir -p /tmp/axiom_proofs && chown axiom:axiom /tmp/axiom_proofs

# Switch to non-root user
USER axiom

# Default environment variables (overrideable at runtime)
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    LOG_FORMAT=json \
    LOG_LEVEL=INFO

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "uvicorn", "axiom.services.api_gateway.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
