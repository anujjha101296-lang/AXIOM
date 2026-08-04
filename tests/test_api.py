import os
import pytest
from fastapi.testclient import TestClient
import tempfile

from axiom.services.api_gateway.main import app
from axiom.services.model_gateway.client import ModelClient

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_ready_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"

def test_auth_protection():
    # Ingest without auth header
    response = client.post("/ingest", json={"arxiv_id": "2303.1234"})
    assert response.status_code == 401
    
    # Query without auth header
    response = client.post("/query", json={"query_string": "test"})
    assert response.status_code == 401

def test_auth_success():
    headers = {"Authorization": "Bearer test_token"}
    
    # Ingest with correct auth header
    response = client.post("/ingest", json={"arxiv_id": "2303.1234"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "triggered"
    assert response.json()["arxiv_id"] == "2303.1234"
    
    # Query with correct auth header
    response = client.post("/query", json={"query_string": "Lagrange's Theorem"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_model_gateway_client():
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_db = os.path.join(temp_dir, "cache.db")
        model_client = ModelClient(cache_path=cache_db)
        
        # Test generation (should return mock response)
        prompt = "Prove that there are infinitely many primes."
        response1 = model_client.generate(prompt, model="gpt-4")
        assert "Proof:" in response1
        
        # Test caching (the second call with same parameters should hit cache)
        # Modify the mock database record to verify it was read from cache
        import sqlite3
        conn = sqlite3.connect(cache_db)
        with conn:
            conn.execute("UPDATE model_cache SET response = 'Cached proof response' WHERE prompt_hash = (SELECT prompt_hash FROM model_cache LIMIT 1);")
        conn.close()
        
        response2 = model_client.generate(prompt, model="gpt-4")
        assert response2 == "Cached proof response"
