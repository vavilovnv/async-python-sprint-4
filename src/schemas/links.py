from pydantic import BaseModel, HttpUrl


class URLBase(BaseModel):
    target_url: HttpUrl

    class Config:
        orm_mode = True


class URL(URLBase):
    short_url: str
    is_active: bool
    clicks: int
