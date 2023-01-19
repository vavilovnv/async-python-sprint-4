import logging.config
from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import LOGGING
from db import get_session
from schemas import links
from services import link_crud

from .utils import validate_link

router = APIRouter()

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('short_url_api_logger')


@router.get(
    '/ping',
    response_model=links.Ping,
    tags=['Service'],
    description='Execute a database ping.'
)
async def check_db(db: AsyncSession = Depends(get_session)) -> Any:
    logger.info('A ping to the DB is requested')
    return await link_crud.get_ping_db(db=db)


@router.get(
    '/{url_id}',
    response_class=RedirectResponse,
    tags=['Links'],
    description='Redirect to the original url, if it exists.'
)
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
    logger.info(
        'Redirect from %s to %s', obj.short_url, obj.original_url
    )
    return obj.original_url


@router.get(
    '/{url_id}/status',
    response_model=Union[
        links.UsagesCount,
        links.LinksUsages
    ],
    tags=['Links'],
    description="Getting the amount of url usage by url_id. With the "
                "'full-info' parameter, the client's host and the time of url "
                "usage are displayed."
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
        logger.info('Sent short status for url_id %s', url_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'usages_count': res}
        )
    logger.info('Sent full status for url_id %s', url_id)
    return res


@router.get(
    '/',
    tags=['Links'],
    description='Displaying the welcome message when navigating to the root '
                'url.'
)
def read_root() -> str:
    logger.info('Root api url is requested')
    return 'Welcome to the URL shortener API'


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=links.ShortUrl,
    tags=['Links'],
    description='Create and return short url for the original url.'
)
async def create_short_url(
        target_url: links.URLBase,
        db: AsyncSession = Depends(get_session)
) -> Any:
    obj = await link_crud.create(db=db, obj_in=target_url)
    logger.info(
        'Created short url %s for %s', obj.short_url, obj.original_url
    )
    return obj


@router.post(
    '/shorten',
    status_code=status.HTTP_201_CREATED,
    response_model=links.MultiShortUrl,
    tags=['Links'],
    description='Create and return the batch short urls for the original url.'
)
async def create_short_urls(
        target_urls: links.MultiUrl,
        db: AsyncSession = Depends(get_session)
) -> Any:
    logger.info('Created a batch links of short url')
    return await link_crud.create_multi(db=db, obj_in=target_urls)


@router.delete(
    '/{url_id}',
    response_model=links.ShortUrl,
    tags=['Links'],
    description='Mark as delete the short url for url_id.'
)
async def delete_short_url(
        url_id: str,
        db: AsyncSession = Depends(get_session)
) -> Any:
    obj = await link_crud.get(db=db, url_id=url_id)
    validate_link(obj=obj)
    await link_crud.delete(db=db, db_obj=obj)
    logger.info('Short url with url_id %s deleted', url_id)
    return obj
