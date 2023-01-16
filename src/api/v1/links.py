import validators

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from schemas import links
from services import link_crud

router = APIRouter()


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


@router.get('/{url_id}', status_code=status.HTTP_307_TEMPORARY_REDIRECT, response_class=RedirectResponse)
async def get_url(
        url_id: str,
        request: Request,
        db: AsyncSession = Depends(get_session)
):
    obj = await link_crud.get(db=db, url_id=url_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Not found'
        )
    if not obj.is_active:
        return Response(status_code=status.HTTP_410_GONE)
    return obj.original_url


@router.get('/')
def read_root():
    return 'Welcome to the URL shortener API'


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=links.ShortUrl
)
async def create_short_url(
        target_url: links.URLBase,
        db: AsyncSession = Depends(get_session)
):
    res = await link_crud.create(db=db, obj_in=target_url)
    return res


@router.post(
    '/shorten',
    status_code=status.HTTP_201_CREATED,
    response_model=links.MultiShortUrl
)
async def create_short_urls(
        target_urls: links.MultiUrl,
        db: AsyncSession = Depends(get_session)
):
    res = await link_crud.create_multi(db=db, obj_in=target_urls)
    return res
