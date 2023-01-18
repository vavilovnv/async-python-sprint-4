import pytest
from fastapi import status
from httpx import AsyncClient

from core.config import SHORT_URL_LENGTH
from main import app

from .utils import COUNT_LINKS, ID_LINKS, LINKS


@pytest.mark.asyncio()
async def test_ping(client: AsyncClient) -> None:
    response = await client.get(
        app.url_path_for("check_db")
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert 'ping_db' in data
    assert data['ping_db'] > 0


@pytest.mark.asyncio()
async def test_create_short_url(client: AsyncClient) -> None:
    response = await client.post(
        app.url_path_for("create_short_url"),
        json={'original_url': LINKS[0]}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert isinstance(data, dict)
    assert 'url_id' in data, 'No field "id" in answer'
    assert 'short_url' in data, 'No field "short_url" in answer'
    assert len(data['url_id']) == SHORT_URL_LENGTH, 'Wrong length url_id'


@pytest.mark.asyncio()
async def test_create_short_urls(client: AsyncClient) -> None:
    response = await client.post(
        app.url_path_for("create_short_urls"),
        json=[{'original_url': link} for link in LINKS]
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == COUNT_LINKS
    assert isinstance(data, list), 'Response for create some links is not list'
    for i, value in enumerate(data):
        ID_LINKS[LINKS[i]] = value['url_id']


@pytest.mark.asyncio()
async def test_get_url(client: AsyncClient) -> None:
    response = await client.get(app.url_path_for(
        "get_url",
        url_id=ID_LINKS[LINKS[0]])
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    message = 'Original url not in header "location"'
    assert LINKS[0] in response.headers.get('Location'), message


@pytest.mark.asyncio()
async def test_delete_url(client: AsyncClient) -> None:
    original_url = LINKS[1]
    await client.delete(
        app.url_path_for("delete_short_url", url_id=ID_LINKS[original_url])
    )
    response = await client.get(
        app.url_path_for("get_url", url_id=ID_LINKS[original_url]),
        follow_redirects=True
    )
    assert response.status_code == status.HTTP_410_GONE


@pytest.mark.asyncio()
async def test_get_url_status(client: AsyncClient) -> None:
    original_url = LINKS[0]
    response = await client.get(
        app.url_path_for("get_url_status", url_id=ID_LINKS[original_url])
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict), 'Response is not dict'
    assert data.get("usages_count")
    assert data["usages_count"] == 1, 'Link usage is not equal 1'
    response = await client.get(
        app.url_path_for("get_url_status", url_id=ID_LINKS[original_url]),
        params='full-info=yes'
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list), 'Response is not list'
    assert len(data) == 1, 'Link usage is not equal 1'
    assert data[0].get("client")
    assert data[0].get("use_at")
