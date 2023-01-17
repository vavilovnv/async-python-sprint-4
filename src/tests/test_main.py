import pytest

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app


COUNT_TESTS = 5
LINKS = [f'http://test_{i}.py' for i in range(COUNT_TESTS)]
ID_LINKS = {}


@pytest.mark.asyncio
async def test_create_item(
    client: AsyncClient, async_session: AsyncSession
) -> None:
    response = await client.post(
        app.url_path_for('create_links'),
        json=[{"original_link": LINKS[i]} for i in range(COUNT_TESTS)]
    )
    assert response.status_code == status.HTTP_201_CREATED
    # assert isinstance(response.json(), list)
    # for item in response.json():
    #     assert 'id' in item, 'No field "id" in answer'
    #     assert 'original_url' in item, 'No field "original_url" in answer'
    #     ID_LINKS.update({item['id']: item['original_url']})
    #     assert 'short_url' in item, 'No field "short_url" in answer'
