import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from axiom.core.models import Base, User, Project, Document
from axiom.core.repositories import UserRepository, ProjectRepository, DocumentRepository

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    # Enforce foreign key constraints for SQLite
    async with test_engine.connect() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.commit()
        
    AsyncSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_database_connection(db_session):
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_user_creation(db_session):
    repo = UserRepository(db_session)
    user = await repo.create(email="test@example.com", hashed_password="hashed")
    assert user.id is not None
    assert user.email == "test@example.com"
    
    fetched = await repo.get_by_email("test@example.com")
    assert fetched.id == user.id

@pytest.mark.asyncio
async def test_project_creation_and_ownership(db_session):
    user_repo = UserRepository(db_session)
    proj_repo = ProjectRepository(db_session)
    
    user = await user_repo.create(email="owner@example.com", hashed_password="pwd")
    project = await proj_repo.create(owner_id=user.id, name="Test Project", description="Desc")
    
    assert project.id is not None
    assert project.owner_id == user.id
    
    projects = await proj_repo.list_for_user(user.id)
    assert len(projects) == 1
    assert projects[0].name == "Test Project"

@pytest.mark.asyncio
async def test_document_creation(db_session):
    user_repo = UserRepository(db_session)
    proj_repo = ProjectRepository(db_session)
    doc_repo = DocumentRepository(db_session)
    
    user = await user_repo.create(email="doc@example.com", hashed_password="pwd")
    project = await proj_repo.create(owner_id=user.id, name="Project")
    document = await doc_repo.create(project_id=project.id, title="Doc 1")
    
    assert document.id is not None
    assert document.project_id == project.id
    
    docs = await doc_repo.list_for_project(project.id)
    assert len(docs) == 1
    assert docs[0].title == "Doc 1"

@pytest.mark.asyncio
async def test_foreign_key_integrity(db_session):
    proj_repo = ProjectRepository(db_session)
    
    # Trying to create a project with a non-existent user should raise an IntegrityError
    with pytest.raises(IntegrityError):
        await proj_repo.create(owner_id="fake-id", name="Invalid Project")

@pytest.mark.asyncio
async def test_rollback_behavior(db_session):
    user_repo = UserRepository(db_session)
    
    # Start a transaction logically within our test
    try:
        user = await user_repo.create(email="rollback@example.com", hashed_password="pwd")
        # Simulate a failure
        raise ValueError("Simulated failure")
    except ValueError:
        await db_session.rollback()
        
    # Check that user is not in DB after rollback
    fetched = await user_repo.get_by_email("rollback@example.com")
    assert fetched is None

@pytest.mark.asyncio
async def test_invalid_input(db_session):
    user_repo = UserRepository(db_session)
    
    await user_repo.create(email="dup@example.com", hashed_password="pwd")
    
    # Trying to create a user with duplicate email should fail (unique constraint)
    with pytest.raises(IntegrityError):
        await user_repo.create(email="dup@example.com", hashed_password="pwd2")

from httpx import AsyncClient, ASGITransport
from axiom.services.api_gateway.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_readiness_check(test_engine):
    app.dependency_overrides = {}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["database"] == "connected"
