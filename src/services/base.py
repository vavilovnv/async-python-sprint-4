import time
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar, Union

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import Base

from .utils import create_obj

ModelType = TypeVar("ModelType", bound=Base)
RequestTypeModel = TypeVar("RequestTypeModel", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
MultiCreateSchemaType = TypeVar("MultiCreateSchemaType", bound=BaseModel)


class Repository(ABC):

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_ping_db(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_status(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create_multi(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create_link_usage(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
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

    async def create(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType
    ) -> ModelType:
        data = jsonable_encoder(obj_in)
        db_object = create_obj(data, self._model)
        try:
            db.add(db_object)
            await db.commit()
        except exc.SQLAlchemyError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error
            )
        await db.refresh(db_object)
        return db_object

    async def create_multi(
            self,
            db: AsyncSession,
            obj_in: MultiCreateSchemaType
    ) -> list[ModelType]:
        list_data = jsonable_encoder(obj_in)
        db_objects = [create_obj(data, self._model) for data in list_data]
        try:
            db.add_all(db_objects)
            await db.commit()
        except exc.SQLAlchemyError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error
            )
        for obj in db_objects:
            await db.refresh(obj)
        return db_objects

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
    ) -> None:
        request_obj = self._request_model(
            link=link_id,
            client=f'{request.client.host}:{request.client.port}'
        )
        db.add(request_obj)
        await db.commit()
        await db.refresh(request_obj)

    async def get_ping_db(self, db: AsyncSession) -> dict[str, float]:
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
