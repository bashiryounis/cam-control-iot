from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------------------#
# SQLite async database URL                #
# ----------------------------------------#
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./camera_db.sqlite3"

# Async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
