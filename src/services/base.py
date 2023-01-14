from secrets import choice
from string import ascii_uppercase
from typing import Any, Generic, Type, TypeVar

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import SHORT_URL_LENGTH
from db.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


def create_short_url(url_length):
    return ''.join([choice(ascii_uppercase) for _ in range(url_length)])


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDBLink(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, id: Any) -> Any:
        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: list[CreateSchemaType]) -> list[ModelType]:
        res = []
        obj_in_data = jsonable_encoder(obj_in)
        for data in obj_in_data:
            data['short_url'] = create_short_url(SHORT_URL_LENGTH)
            data['clicks'] = 0
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
