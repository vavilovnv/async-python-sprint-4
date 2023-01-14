import os

from dotenv import load_dotenv
from logging import config as logging_config
from pathlib import Path
from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)

load_dotenv(dotenv_path=Path('../.env'))


class AppSettings(BaseSettings):
    app_title: str = "Url shortener API"
    database_dsn: PostgresDsn = os.getenv(
        'DATABASE_DSN',
        'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres'
    )
    project_host: str = os.getenv('PROJECT_HOST', '0.0.0.0')
    project_port: int = int(os.getenv('PROJECT_PORT', '8000'))

    class Config:
        env_file = '.env'


app_settings = AppSettings()
BASE_DIR = Path(__file__).parent.parent
