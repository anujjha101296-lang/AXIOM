import pytest
import pytest_asyncio
import io
from httpx import AsyncClient, ASGITransport
from axiom.services.api_gateway.main import app
from axiom.core.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def setup_db():
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
async def test_document_upload_and_extraction(setup_db):
    app.dependency_overrides = {}
    from axiom.core.database import get_db
    # We must explicitly re-assign the override for the test due to how app.dependency_overrides is reset
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and Login
        await client.post("/auth/register", json={"email": "doc@ax.com", "password": "pass"})
        res_login = await client.post("/auth/login", data={"username": "doc@ax.com", "password": "pass"})
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create Project
        res_proj = await client.post("/projects", json={"name": "Doc Project"}, headers=headers)
        assert res_proj.status_code == 201
        project_id = res_proj.json()["id"]
        
        # Create a fake PDF file bytes using reportlab or just standard PDF header (pypdf needs a valid PDF structure)
        # For the sake of the test, we'll use a tiny base64 encoded empty PDF
        import base64
        empty_pdf_b64 = "JVBERi0xLjcKCjEgMCBvYmogICUgZW50cnkgcG9pbnQKPDwKICAvVHlwZSAvQ2F0YWxvZwogIC9QYWdlcyAyIDAgUgo+PgplbmRvYmoKCjIgMCBvYmoKPDwKICAvVHlwZSAvUGFnZXMKICAvTWVkaWFCb3ggWyAwIDAgMjAwIDIwMCBdCiAgL0NvdW50IDEKICAvS2lkcyBbIDMgMCBSIF0KPj4KZW5kb2JqCgozIDAgb2JqCjw8CiAgL1R5cGUgL1BhZ2UKICAvUGFyZW50IDIgMCBSCiAgL1Jlc291cmNlcyA8PAogICAgL0ZvbnQgPDwKICAgICAgL0YxIDQgMCBSCgkgICAgPj4KICA+PgogIC9Db250ZW50cyA1IDAgUgo+PgplbmRvYmoKCjQgMCBvYmoKPDwKICAvVHlwZSAvRm9udAogIC9TdWJ0eXBlIC9UeXBlMQogIC9CYXNlRm9udCAvVGltZXMtUm9tYW4KPj4KZW5kb2JqCgo1IDAgb2JqICAlIHBhZ2UgY29udGVudAo8PAogIC9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCjcwIDUwIFRECi9GMSAxMiBUZmoKKEhlbGxvLCB3b3JsZCEpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAwMDAwMDc5IDAwMDAwIG4gCjAwMDAwMDAxNzMgMDAwMDAgbiAKMDAwMDAwMDMwMSAwMDAwMCBuIAowMDAwMDAwMzgwIDAwMDAwIG4gCnRyYWlsZXIKPDwKICAvU2l6ZSA2CiAgL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQ5MgolJUVPRgo="
        pdf_bytes = base64.b64decode(empty_pdf_b64)
        
        files = {"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        
        # Upload Document
        res_upload = await client.post(f"/projects/{project_id}/documents", headers=headers, files=files)
        assert res_upload.status_code == 201
        
        doc_id = res_upload.json()["id"]
        assert res_upload.json()["status"] == "completed"
        
        # List Documents
        res_list = await client.get(f"/projects/{project_id}/documents", headers=headers)
        assert res_list.status_code == 200
        assert len(res_list.json()) == 1
        
        # Get Document Detail
        res_detail = await client.get(f"/projects/{project_id}/documents/{doc_id}", headers=headers)
        assert res_detail.status_code == 200
        assert res_detail.json()["title"] == "test.pdf"
