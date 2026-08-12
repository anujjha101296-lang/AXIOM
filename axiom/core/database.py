from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from axiom.config import settings

# In tests or local dev without Postgres, fallback to SQLite if DB_PATH is set
# settings.database_url might be missing or set to sqlite:///./axiom.db in .env
database_url = settings.database_url if hasattr(settings, 'database_url') else None

if not database_url:
    db_path = getattr(settings, 'db_path', './axiom.db')
    database_url = f"sqlite+aiosqlite:///{db_path}"
else:
    # Ensure aiosqlite is used for sqlite urls if someone passed sqlite:///
    if database_url.startswith("sqlite:///") and not database_url.startswith("sqlite+aiosqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    database_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    """Dependency to yield a database session with transaction management."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
