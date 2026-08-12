import pytest
import pytest_asyncio
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
async def test_auth_and_projects(setup_db):
    # This acts as our Phase 2 Integration Test
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register User
        res_register = await client.post("/auth/register", json={"email": "test@ax.com", "password": "pass"})
        assert res_register.status_code == 200, res_register.text
        assert res_register.json()["email"] == "test@ax.com"
        
        # 2. Duplicate Registration fails
        res_dup = await client.post("/auth/register", json={"email": "test@ax.com", "password": "pass"})
        assert res_dup.status_code == 400
        
        # 3. Login User
        res_login = await client.post("/auth/login", data={"username": "test@ax.com", "password": "pass"})
        assert res_login.status_code == 200
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 4. GET /auth/me
        res_me = await client.get("/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["email"] == "test@ax.com"
        
        # 5. Create Project
        res_proj = await client.post("/projects", json={"name": "Alpha", "description": "Desc"}, headers=headers)
        assert res_proj.status_code == 201
        project_id = res_proj.json()["id"]
        assert res_proj.json()["name"] == "Alpha"
        
        # 6. List Projects
        res_list = await client.get("/projects", headers=headers)
        assert res_list.status_code == 200
        assert len(res_list.json()) == 1
        
        # 7. Update Project
        res_patch = await client.patch(f"/projects/{project_id}", json={"name": "Beta"}, headers=headers)
        assert res_patch.status_code == 200
        assert res_patch.json()["name"] == "Beta"
        
        # 8. Delete Project
        res_del = await client.delete(f"/projects/{project_id}", headers=headers)
        assert res_del.status_code == 204
        
        # 9. Get Project (should be 404)
        res_get = await client.get(f"/projects/{project_id}", headers=headers)
        assert res_get.status_code == 404
