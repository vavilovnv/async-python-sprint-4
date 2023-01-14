from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

from core.config import SHORT_URL_LENGTH

Base = declarative_base()


class Links(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    target_url = Column(String(1000), nullable=False)
    short_url = Column(String(SHORT_URL_LENGTH), nullable=False)
    clicks = Column(Integer)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
