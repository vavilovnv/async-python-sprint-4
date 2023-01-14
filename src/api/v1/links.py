import validators

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from schemas import links
from services import link_crud

router = APIRouter()


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


@router.get('/')
def read_root():
    return 'Welcome to the URL shortener API'


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=list[links.URL]
)
async def create_short_urls(
        target_urls: list[links.URLBase],
        db: AsyncSession = Depends(get_session)
):
    res = await link_crud.create(db=db, obj_in=target_urls)
    return res
