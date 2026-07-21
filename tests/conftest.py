import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database.models import User
from app.database.base import Base
from app.database.session import get_session
from app.database import redis as redis_module

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


class FakeRedis:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value, ex=None):
        self.data["key"] = value


@pytest_asyncio.fixture
def fake_redis():
    return FakeRedis()


@pytest_asyncio.fixture
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session, fake_redis):
    async def overide_get_session():
        yield db_session

    app.dependency_overrides[get_session] = overide_get_session
    redis_module.client = fake_redis

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="https://test") as ac:
        yield ac

    app.dependency_overrides.clear()

