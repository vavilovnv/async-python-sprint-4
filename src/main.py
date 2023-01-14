import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import links
from core.config import app_settings


app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    redoc_url=None
)

app.include_router(links.router, prefix='/api/v1', tags=['Links'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
    )
