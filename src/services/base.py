import time
from secrets import choice
from string import ascii_uppercase
from typing import Any, Generic, Optional, Type, TypeVar, Union

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import SHORT_URL_LENGTH, app_settings
from db import Base

ModelType = TypeVar("ModelType", bound=Base)
RequestTypeModel = TypeVar("RequestTypeModel", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
MultiCreateSchemaType = TypeVar("MultiCreateSchemaType", bound=BaseModel)


def create_short_url(url_length):
    return ''.join([choice(ascii_uppercase) for _ in range(url_length)])


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_ping_db(self, *args, **kwargs):
        raise NotImplementedError

    def get_status(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def create_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create_link_usage(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDBLink(
    Repository,
    Generic[
        ModelType,
        RequestTypeModel,
        CreateSchemaType,
        MultiCreateSchemaType
    ]
):

    def __init__(self, model: Type[ModelType], request: Type[ModelType]):
        self._model = model
        self._request_model = request

    async def get(self, db: AsyncSession, url_id: Any) -> Any:
        statement = select(self._model).where(self._model.url_id == url_id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        data = jsonable_encoder(obj_in)
        short_form = create_short_url(SHORT_URL_LENGTH)
        data['url_id'] = short_form
        data['usages_count'] = 0
        data['short_url'] = f'http://{app_settings.project_host}:{app_settings.project_port}/api/v1/{short_form}'
        db_obj = self._model(**data)
        try:
            db.add(db_obj)
            await db.commit()
        except exc.SQLAlchemyError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error
            )
        await db.refresh(db_obj)
        return db_obj

    async def create_multi(self, db: AsyncSession, obj_in: MultiCreateSchemaType) -> list[ModelType]:
        res = []
        obj_in_data = jsonable_encoder(obj_in)
        for data in obj_in_data:
            short_form = create_short_url(SHORT_URL_LENGTH)
            data['url_id'] = short_form
            data['usages_count'] = 0
            data['short_url'] = f'http://{app_settings.project_host}:{app_settings.project_port}/api/v1/{short_form}'
            db_obj = self._model(**data)
            try:
                db.add(db_obj)
                await db.commit()
            except exc.SQLAlchemyError as error:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error
                )
            await db.refresh(db_obj)
            res.append(db_obj)
        return res

    @staticmethod
    async def delete(db: AsyncSession, db_obj: ModelType) -> None:
        setattr(db_obj, 'is_active', False)
        await db.commit()

    @staticmethod
    async def update_usage_count(db: AsyncSession, db_obj: ModelType) -> None:
        db_obj.usages_count += 1
        await db.commit()
        await db.refresh(db_obj)

    async def create_link_usage(
            self,
            db: AsyncSession,
            link_id: int,
            request: Request
    ):
        request_obj = self._request_model(
            link=link_id,
            client=f'{request.client.host}:{request.client.port}'
        )
        db.add(request_obj)
        await db.commit()
        await db.refresh(request_obj)

    async def get_ping_db(self, db: AsyncSession):
        start = time.time()
        statement = select(self._model)
        await db.execute(statement=statement)
        return {'ping_db': '{:.5f}'.format(time.time() - start)}

    async def get_status(
            self,
            db: AsyncSession,
            db_obj: ModelType,
            limit: int,
            offset: int,
            full_info: Optional[bool],
    ) -> Union[int, list[ModelType]]:
        if not full_info:
            return db_obj.usages_count
        statement = select(
            self._request_model
        ).where(
            self._request_model.link == db_obj.id
        ).offset(offset).limit(limit)
        res = await db.execute(statement=statement)
        return res.scalars().all()
