from pydantic import HttpUrl
from shortuuid import ShortUUID
from sqlalchemy.orm import DeclarativeMeta

from core.config import app_settings
from models.links import Link


def create_short_url(url_length: int) -> str:
    return ShortUUID().random(length=url_length)


def create_obj(
        obj_in_data: dict[str, [HttpUrl, str, int]],
        model: DeclarativeMeta
) -> Link:
    add_obj_info = {}
    short_form = create_short_url(app_settings.short_url_length)
    add_obj_info['url_id'] = short_form
    short_url = (f'http://{app_settings.project_host}:'
                 f'{app_settings.project_port}/api/v1/{short_form}')
    add_obj_info['short_url'] = short_url
    add_obj_info['usages_count'] = 0
    obj_in_data.update(add_obj_info)
    return model(**obj_in_data)
