# AXIOM Backend Production Dockerfile
FROM python:3.12-slim

# Create a non-root user
RUN groupadd -r axiom && useradd -r -g axiom axiom

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    z3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml
COPY pyproject.toml .

# Install dependencies using pip
RUN pip install --no-cache-dir .

# Copy application code
COPY axiom/ ./axiom/

# Environment configuration
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# Change ownership
RUN chown -R axiom:axiom /app

# Switch to non-root user
USER axiom

# Expose port
EXPOSE 8000

# Graceful shutdown is managed by Uvicorn
CMD ["sh", "-c", "uvicorn axiom.services.api_gateway.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4 --log-level info"]
