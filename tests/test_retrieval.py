import pytest
import pytest_asyncio
import io
import base64
from httpx import AsyncClient, ASGITransport
from axiom.services.api_gateway.main import app
from axiom.core.models import Base
from sqlalchemy.ext.asyncio import create_async_engine
import os

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def setup_db():
    # Force Mock Provider
    os.environ["ENVIRONMENT"] = "test"
    
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    from sqlalchemy.ext.asyncio import async_sessionmaker
    AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async def override_get_db():
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
                
    from axiom.core.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_semantic_retrieval_and_isolation(setup_db):
    app.dependency_overrides = {}
    from axiom.core.database import get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User 1 Setup
        await client.post("/auth/register", json={"email": "u1@ax.com", "password": "pass"})
        res_l1 = await client.post("/auth/login", data={"username": "u1@ax.com", "password": "pass"})
        t1 = res_l1.json()["access_token"]
        h1 = {"Authorization": f"Bearer {t1}"}
        
        # User 2 Setup
        await client.post("/auth/register", json={"email": "u2@ax.com", "password": "pass"})
        res_l2 = await client.post("/auth/login", data={"username": "u2@ax.com", "password": "pass"})
        t2 = res_l2.json()["access_token"]
        h2 = {"Authorization": f"Bearer {t2}"}
        
        # Create Project for User 1
        res_proj = await client.post("/projects", json={"name": "Retrieval Project"}, headers=h1)
        assert res_proj.status_code == 201
        project_id = res_proj.json()["id"]
        
        # Create a tiny dummy PDF
        empty_pdf_b64 = "JVBERi0xLjcKCjEgMCBvYmogICUgZW50cnkgcG9pbnQKPDwKICAvVHlwZSAvQ2F0YWxvZwogIC9QYWdlcyAyIDAgUgo+PgplbmRvYmoKCjIgMCBvYmoKPDwKICAvVHlwZSAvUGFnZXMKICAvTWVkaWFCb3ggWyAwIDAgMjAwIDIwMCBdCiAgL0NvdW50IDEKICAvS2lkcyBbIDMgMCBSIF0KPj4KZW5kb2JqCgozIDAgb2JqCjw8CiAgL1R5cGUgL1BhZ2UKICAvUGFyZW50IDIgMCBSCiAgL1Jlc291cmNlcyA8PAogICAgL0ZvbnQgPDwKICAgICAgL0YxIDQgMCBSCgkgICAgPj4KICA+PgogIC9Db250ZW50cyA1IDAgUgo+PgplbmRvYmoKCjQgMCBvYmoKPDwKICAvVHlwZSAvRm9udAogIC9TdWJ0eXBlIC9UeXBlMQogIC9CYXNlRm9udCAvVGltZXMtUm9tYW4KPj4KZW5kb2JqCgo1IDAgb2JqICAlIHBhZ2UgY29udGVudAo8PAogIC9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCjcwIDUwIFRECi9GMSAxMiBUZmoKKEhlbGxvLCB3b3JsZCEpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAwMDAwMDc5IDAwMDAwIG4gCjAwMDAwMDAxNzMgMDAwMDAgbiAKMDAwMDAwMDMwMSAwMDAwMCBuIAowMDAwMDAwMzgwIDAwMDAwIG4gCnRyYWlsZXIKPDwKICAvU2l6ZSA2CiAgL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQ5MgolJUVPRgo="
        pdf_bytes = base64.b64decode(empty_pdf_b64)
        
        # Upload Document
        files = {"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        res_upload = await client.post(f"/projects/{project_id}/documents", headers=h1, files=files)
        assert res_upload.status_code == 201
        
        # The upload response should indicate indexing is complete or processing
        # Wait, the Backend Agent is making the process synchronous for MVP
        doc_data = res_upload.json()
        assert "indexing_status" in doc_data
        assert doc_data["indexing_status"] == "INDEXED"
        
        # Search via User 1
        res_search = await client.post(f"/projects/{project_id}/search", json={"query": "hello", "limit": 5}, headers=h1)
        assert res_search.status_code == 200
        search_data = res_search.json()
        assert len(search_data) > 0
        assert "Hello, world!" in search_data[0]["content"]
        assert "score" in search_data[0]
        
        # Attempt Search via User 2 (Should Fail due to Isolation)
        res_search_u2 = await client.post(f"/projects/{project_id}/search", json={"query": "hello", "limit": 5}, headers=h2)
        assert res_search_u2.status_code in [403, 404]
