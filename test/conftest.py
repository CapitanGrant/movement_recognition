import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.opencv_cam.models import Base
from app.config import get_database_url
from app.dao.session_maker import DatabaseSessionManager, session_manager
from app.main import app


TEST_DB_URL = os.getenv("TEST_DB_URL", get_database_url(for_tests=True))

test_engine = create_async_engine(
    TEST_DB_URL,
    future=True,
    echo=False,
    poolclass=NullPool,
)

TestingSessionLocal = DatabaseSessionManager(
    async_sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    ))


async def override_db():
    async with TestingSessionLocal.create_session() as session:
        yield session


@pytest_asyncio.fixture(autouse=True, scope="function")
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    app.dependency_overrides = {}
    app.dependency_overrides[session_manager.get_session] = override_db
    app.dependency_overrides[session_manager.get_transaction_session] = override_db
    with TestClient(app) as client:
        yield client


