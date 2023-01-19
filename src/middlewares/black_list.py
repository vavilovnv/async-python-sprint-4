import logging.config
from typing import Callable

from fastapi import Request, Response, status

from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('short_url_api_logger')


class BlackListMiddleware:

    def __init__(self, black_list: list[str]):
        self._black_list = black_list

    async def __call__(
            self,
            request: Request,
            call_next: Callable
    ) -> Response:
        if request.client and request.client.host not in self._black_list:
            return await call_next(request)
        logger.info(
            'Request from client %s in black list', request.client.host
        )
        return Response(
            'Access is denied.',
            status_code=status.HTTP_403_FORBIDDEN
        )
