import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

import asyncpg
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db import get_session
from main import app
from models.links import Link

from .utils import TEST_DB_NAME, database_dsn


@pytest_asyncio.fixture(scope='function')
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, follow_redirects=False,
                           base_url='http://localhost') as async_client:
        yield async_client


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


async def create_test_db() -> None:
    user, password, database = 'postgres', 'postgres', TEST_DB_NAME
    try:
        await asyncpg.connect(database=database, user=user, password=password)
    except asyncpg.InvalidCatalogNameError:
        conn = await asyncpg.connect(database='postgres', user=user,
                                     password=password)
        sql_command = text(f'CREATE DATABASE "{database}" '
                           f'OWNER "{user}" ENCODING "utf8"')
        await conn.execute(sql_command)
        await conn.close()
        await asyncpg.connect(database=database, user=user, password=password)


@pytest_asyncio.fixture(scope="module")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    await create_test_db()
    engine = create_async_engine(database_dsn, echo=False, future=True)
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Link.metadata.drop_all)
        await conn.run_sync(Link.metadata.create_all)
    async with session() as session:
        def get_session_override():
            return session
        app.dependency_overrides[get_session] = get_session_override
        yield session
    await engine.dispose()
