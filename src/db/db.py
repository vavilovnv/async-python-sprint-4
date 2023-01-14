from core.config import app_settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


engine = create_async_engine(
    app_settings.database_dsn,
    echo=True,  # перед сдачей на ревью отключить
    future=True
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()
