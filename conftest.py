# conftest.py

import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database.base import Base
from app.database.session import get_db


SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def engine():
    return create_async_engine(SQLALCHEMY_TEST_DATABASE_URL)


@pytest.fixture(scope="module")
async def database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session(engine, database):
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            class_=AsyncSession
        )()

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest.fixture()
def client(db_session):
    async def override_get_db():
        yield db_session  # yield вместо return, и async def

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

