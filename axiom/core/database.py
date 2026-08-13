"""Database configuration and session dependency for AXIOM."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from axiom.config import settings
from axiom.core.models import Base

# Module level fallback sync engine sharing a single in-memory DB via StaticPool
sync_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
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
                    def all(self):
                        return sc.all()

                    def first(self):
                        return sc.first()

                    def one_or_none(self):
                        return sc.one_or_none()

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


# Try creating async engine
database_url = settings.database_url if hasattr(settings, 'database_url') else None

if not database_url:
    db_path = getattr(settings, 'db_path', './axiom.db')
    database_url = f"sqlite+aiosqlite:///{db_path}"
else:
    if database_url.startswith("sqlite:///") and not database_url.startswith("sqlite+aiosqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

try:
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
except Exception:
    engine = None
    AsyncSessionLocal = None


async def get_db():
    """Dependency to yield a database session with transaction management."""
    if AsyncSessionLocal is not None:
        try:
            async with AsyncSessionLocal() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
            return
        except Exception:
            pass

    # Fallback to module-level sync engine wrapper
    sess = SyncSessionLocal()
    async with AsyncSessionWrapper(sess) as s:
        yield s
