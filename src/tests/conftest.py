import asyncio
import asyncpg

import pytest
import pytest_asyncio

from typing import AsyncGenerator, Generator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


from db import Base, get_session
from main import app


BASE_URL = '127.0.0.1'
TEST_DB_NAME = "db_tests"
database_dsn = "postgresql+asyncpg://postgres:postgres@localhost:5432/db_tests"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


async def _create_test_db() -> None:
    user, password, database = 'postgres', 'postgres', TEST_DB_NAME
    try:
        await asyncpg.connect(database=database, user=user, password=password)
    except asyncpg.InvalidCatalogNameError:
        conn = await asyncpg.connect(database='postgres', user=user,
                                     password=password)
        await conn.execute(f'CREATE DATABASE "{database}" OWNER "{user}"')
        await conn.close()
        await asyncpg.connect(database=database, user=user, password=password)


@pytest_asyncio.fixture(scope='function')
async def client() -> AsyncGenerator:
    async with AsyncClient(app=app, follow_redirects=False,
                           base_url=BASE_URL) as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="module")
async def async_session() -> AsyncGenerator:
    await _create_test_db()
    engine = create_async_engine(database_dsn, echo=True, future=True)
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with session() as s:
        def get_session_override():
            return s
        app.dependency_overrides[get_session] = get_session_override
        yield s

    await engine.dispose()
