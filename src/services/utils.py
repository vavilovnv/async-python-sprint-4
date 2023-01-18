from pydantic import HttpUrl
from shortuuid import ShortUUID

from core.config import SHORT_URL_LENGTH, app_settings


def create_short_url(url_length: int) -> str:
    return ShortUUID().random(length=url_length)


def extend_data(data: dict[str, [HttpUrl, str, 0]]) -> None:
    short_form = create_short_url(SHORT_URL_LENGTH)
    data['url_id'] = short_form
    data['usages_count'] = 0
    short_url = (f'http://{app_settings.project_host}:'
                 f'{app_settings.project_port}/api/v1/{short_form}')
    data['short_url'] = short_url
