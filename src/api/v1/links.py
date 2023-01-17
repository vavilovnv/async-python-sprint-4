from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from models import Link
from schemas import links
from services import link_crud

router = APIRouter()


def validate_link(obj: Link) -> None:
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Url not found'
        )
    if not obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail='Url deleted'
        )


@router.get('/ping', response_model=links.Ping, tags=['Service'])
async def check_db(db: AsyncSession = Depends(get_session)) -> Any:
    res = await link_crud.get_ping_db(db=db)
    return res


@router.get(
    '/{url_id}',
    response_class=RedirectResponse)
async def get_url(
        url_id: str,
        request: Request,
        db: AsyncSession = Depends(get_session)
) -> Any:
    obj = await link_crud.get(db=db, url_id=url_id)
    validate_link(obj=obj)
    await link_crud.update_usage_count(db=db, db_obj=obj)
    await link_crud.create_link_usage(
        db=db,
        link_id=obj.id,
        request=request
    )
    return obj.original_url


@router.get(
    '/{url_id}/status',
    response_model=Union[
        links.UsagesCount,
        links.LinksUsages
    ]
)
async def get_url_status(
        url_id: str,
        full_info: Optional[bool] = Query(default=None, alias='full-info'),
        max_size: int = Query(
            default=10,
            ge=1,
            alias='max-size',
            description='Query max size.'
        ),
        offset: int = Query(
            default=0,
            ge=0,
            description='Query offset.'
        ),
        db: AsyncSession = Depends(get_session),
) -> Any:
    obj = await link_crud.get(db=db, url_id=url_id)
    validate_link(obj=obj)
    res = await link_crud.get_status(
        db=db,
        db_obj=obj,
        limit=max_size,
        offset=offset,
        full_info=full_info
    )
    if isinstance(res, int):
        return JSONResponse(status_code=status.HTTP_200_OK, content={'usages_count': res})
    return res


@router.get('/')
def read_root() -> str:
    return 'Welcome to the URL shortener API'


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=links.ShortUrl
)
async def create_short_url(
        target_url: links.URLBase,
        db: AsyncSession = Depends(get_session)
) -> Any:
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
) -> Any:
    res = await link_crud.create_multi(db=db, obj_in=target_urls)
    return res


@router.delete(
    '/{url_id}',
    response_model=links.ShortUrl
)
async def delete_short_url(
        url_id: str,
        db: AsyncSession = Depends(get_session)
) -> Any:
    obj = await link_crud.get(db=db, url_id=url_id)
    validate_link(obj=obj)
    await link_crud.delete(db=db, db_obj=obj)
    return obj
