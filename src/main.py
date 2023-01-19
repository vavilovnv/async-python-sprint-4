import multiprocessing

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api import links
from core.config import StandaloneApplication, app_settings
from middlewares.black_list import BlackListMiddleware

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    redoc_url=None
)

app.include_router(links.router, prefix='/api/v1')

black_list_mw = BlackListMiddleware(black_list=app_settings.black_list)
app.add_middleware(BaseHTTPMiddleware, dispatch=black_list_mw)

if __name__ == '__main__':
    """
    Не уверен, что реализация ниже верная, но мне она показалась более всего
    понятной из того, что удалось нагуглить и накопать в документации.
    """
    options = {
        "bind": f'{app_settings.project_host}:{app_settings.project_port}',
        "workers": multiprocessing.cpu_count(),
        "worker_class": "uvicorn.workers.UvicornWorker",
    }
    StandaloneApplication('main:app', options).run()
