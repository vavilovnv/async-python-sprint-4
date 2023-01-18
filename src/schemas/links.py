from datetime import datetime

from pydantic import BaseModel, HttpUrl


class URLBase(BaseModel):
    original_url: HttpUrl

    class Config:
        orm_mode = True


class MultiUrl(BaseModel):
    __root__: list[URLBase]


class ShortUrl(BaseModel):
    url_id: str
    short_url: HttpUrl

    class Config:
        orm_mode = True


class MultiShortUrl(BaseModel):
    __root__: list[ShortUrl]


class ShortUrlInfo(ShortUrl):
    is_active: bool
    created_at: datetime


class LinkUsage(BaseModel):
    use_at: datetime
    client: str

    class Config:
        orm_mode = True


class Ping(BaseModel):
    ping_db: float


class UsagesCount(BaseModel):
    usages_count: int


class LinkUsage(BaseModel):
    use_at: datetime
    client: str

    class Config:
        orm_mode = True


class LinksUsages(BaseModel):
    __root__: list[LinkUsage]
