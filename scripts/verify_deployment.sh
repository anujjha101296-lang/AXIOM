#!/bin/bash
set -e

echo "Running Deployment Verification Gate..."

echo "1. Testing Python Import..."
PYTHONPATH=. .venv312/bin/python -c "from axiom.services.api_gateway.main import app; print('FastAPI imported successfully')"

echo "2. Building Frontend..."
cd ui && npm install && npm run build
cd ..

echo "3. Testing Backend DB Startup..."
PYTHONPATH=. .venv312/bin/python -c "from axiom.core.knowledge_graph.db import EpistemicStore; store = EpistemicStore(':memory:'); print('DB started successfully')"

echo "Deployment Verification Passed!"
