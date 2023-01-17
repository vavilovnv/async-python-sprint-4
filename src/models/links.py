from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from db import Base


class Link(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    original_url = Column(URLType, nullable=False)
    short_url = Column(URLType, nullable=False)
    url_id = Column(String(8), index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    usages_count = Column(Integer)
    link_usages = relationship('LinksUsage', cascade="all, delete")


class LinksUsage(Base):
    __tablename__ = "links_usages"
    id = Column(Integer, primary_key=True)
    link = Column(Integer, ForeignKey('links.id'))
    client = Column(String, nullable=False)
    use_at = Column(DateTime, index=True, default=datetime.utcnow)
