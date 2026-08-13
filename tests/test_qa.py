import contextlib
import sys

try:
    import pytest
except ImportError:
    class PytestStub:
        class mark:
            @staticmethod
            def asyncio(func):
                return func

            @staticmethod
            def parametrize(argnames, argvalues):
                def decorator(func):
                    func._parametrize = (argnames, argvalues)
                    return func
                return decorator

        @staticmethod
        @contextlib.contextmanager
        def raises(expected_exception):
            class ExcInfo:
                value = None

            exc_info = ExcInfo()
            try:
                yield exc_info
            except expected_exception as e:
                exc_info.value = e
            except Exception as e:
                raise AssertionError(f"Expected {expected_exception}, got {type(e)}") from e
            else:
                raise AssertionError(f"Expected {expected_exception}, but no exception was raised.")

    pytest = PytestStub()
    sys.modules["pytest"] = pytest

try:
    import pytest_asyncio
except ImportError:
    class PytestAsyncioStub:
        @staticmethod
        def fixture(*args, **kwargs):
            def decorator(func):
                return func
            return decorator

    pytest_asyncio = PytestAsyncioStub()
    sys.modules["pytest_asyncio"] = pytest_asyncio

import io
import base64
import os
from httpx import AsyncClient, ASGITransport
from axiom.services.api_gateway.main import app
from axiom.core.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def setup_db():
    # Force Mock Providers
    os.environ["ENVIRONMENT"] = "test"
    
    try:
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
    except Exception:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool
        sync_engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(sync_engine)
        SyncSessionLocal = sessionmaker(bind=sync_engine)

        class AsyncSessionWrapper:
            def __init__(self, sync_session):
                self.sync = sync_session
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if exc_type:
                    self.sync.rollback()
                else:
                    self.sync.commit()
                self.sync.close()
            async def commit(self):
                self.sync.commit()
            async def rollback(self):
                self.sync.rollback()
            async def flush(self):
                self.sync.flush()
            def add(self, instance):
                self.sync.add(instance)
            def add_all(self, instances):
                self.sync.add_all(instances)
            async def execute(self, statement, *args, **kwargs):
                res = self.sync.execute(statement, *args, **kwargs)
                class AsyncResult:
                    def scalars(self):
                        sc = res.scalars()
                        class AsyncScalars:
                            def all(self): return sc.all()
                            def first(self): return sc.first()
                            def one_or_none(self): return sc.one_or_none()
                        return AsyncScalars()
                    def scalar_one_or_none(self):
                        return res.scalar_one_or_none()
                    def all(self):
                        return res.all()
                    def first(self):
                        return res.first()
                return AsyncResult()
            async def refresh(self, instance):
                self.sync.refresh(instance)

        async def override_get_db_sync():
            sess = SyncSessionLocal()
            async with AsyncSessionWrapper(sess) as s:
                yield s

        from axiom.core.database import get_db
        app.dependency_overrides[get_db] = override_get_db_sync
        yield sync_engine
        Base.metadata.drop_all(sync_engine)
        app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_evidence_backed_qa(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User Setup
        await client.post("/auth/register", json={"email": "u1@ax.com", "password": "SecurePass123!"})
        res_l1 = await client.post("/auth/login", data={"username": "u1@ax.com", "password": "SecurePass123!"})
        h1 = {"Authorization": f"Bearer {res_l1.json()['access_token']}"}
        
        # User 2 Setup
        await client.post("/auth/register", json={"email": "u2@ax.com", "password": "SecurePass123!"})
        res_l2 = await client.post("/auth/login", data={"username": "u2@ax.com", "password": "SecurePass123!"})
        h2 = {"Authorization": f"Bearer {res_l2.json()['access_token']}"}

        # Project 1
        res_proj = await client.post("/projects", json={"name": "QA Project"}, headers=h1)
        assert res_proj.status_code == 201
        project_id = res_proj.json()["id"]

        # Question on Empty Project -> Insufficient Evidence
        res_empty = await client.post(f"/projects/{project_id}/research/query", json={"query": "test"}, headers=h1)
        assert res_empty.status_code == 200
        assert "Insufficient evidence" in res_empty.json()["answer"]
        assert len(res_empty.json()["citations"]) == 0

        # Upload tiny PDF
        empty_pdf_b64 = "JVBERi0xLjcKCjEgMCBvYmogICUgZW50cnkgcG9pbnQKPDwKICAvVHlwZSAvQ2F0YWxvZwogIC9QYWdlcyAyIDAgUgo+PgplbmRvYmoKCjIgMCBvYmoKPDwKICAvVHlwZSAvUGFnZXMKICAvTWVkaWFCb3ggWyAwIDAgMjAwIDIwMCBdCiAgL0NvdW50IDEKICAvS2lkcyBbIDMgMCBSIF0KPj4KZW5kb2JqCgozIDAgb2JqCjw8CiAgL1R5cGUgL1BhZ2UKICAvUGFyZW50IDIgMCBSCiAgL1Jlc291cmNlcyA8PAogICAgL0ZvbnQgPDwKICAgICAgL0YxIDQgMCBSCgkgICAgPj4KICA+PgogIC9Db250ZW50cyA1IDAgUgo+PgplbmRvYmoKCjQgMCBvYmoKPDwKICAvVHlwZSAvRm9udAogIC9TdWJ0eXBlIC9UeXBlMQogIC9CYXNlRm9udCAvVGltZXMtUm9tYW4KPj4KZW5kb2JqCgo1IDAgb2JqICAlIHBhZ2UgY29udGVudAo8PAogIC9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCjcwIDUwIFRECi9GMSAxMiBUZmoKKEhlbGxvLCB3b3JsZCEpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAwMDAwMDc5IDAwMDAwIG4gCjAwMDAwMDAxNzMgMDAwMDAgbiAKMDAwMDAwMDMwMSAwMDAwMCBuIAowMDAwMDAwMzgwIDAwMDAwIG4gCnRyYWlsZXIKPDwKICAvU2l6ZSA2CiAgL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQ5MgolJUVPRgo="
        pdf_bytes = base64.b64decode(empty_pdf_b64)
        files = {"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        res_upload = await client.post(f"/projects/{project_id}/documents", headers=h1, files=files)
        assert res_upload.status_code == 201

        # Question on Populated Project -> Grounded QA
        res_qa = await client.post(f"/projects/{project_id}/research/query", json={"query": "test"}, headers=h1)
        assert res_qa.status_code == 200
        data = res_qa.json()
        assert "Mock Answer" in data["answer"]
        
        # Test Multi-tenant Security: User 2 cannot access Project 1 QA
        res_qa_bad = await client.post(f"/projects/{project_id}/research/query", json={"query": "test"}, headers=h2)
        assert res_qa_bad.status_code in [403, 404]
