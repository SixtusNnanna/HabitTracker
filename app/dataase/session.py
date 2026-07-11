from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from sqlalchemy import event

from app.config import settings
from app.dataase.base import Base


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug
)


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

