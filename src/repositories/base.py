from typing import Any, Sequence
import logging

from asyncpg.exceptions import UniqueViolationError
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from sqlalchemy import insert, select, update
from sqlalchemy.exc import NoResultFound

from src.exceptions import (
    ObjectNotFoundException,
    ObjectAlreadyExistsException,
)
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session) -> None:
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args: tuple, **kwargs: dict) -> list:
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by: dict) -> BaseModel | None | Any:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None

        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by: dict) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException

        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        try:
            stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(stmt)
            model = result.scalars().one()
        except IntegrityError as ex:
            logging.error(
                f"Не удалось добавить данные в бд, {data=}, тип ошибки: {type(ex.orig.__cause__)=}"
            )
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExistsException from ex

            logging.error(f"Незнакомая ошибка, тип ошибки: {type(ex.orig.__cause__)=}")
            raise ex

        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: Sequence[BaseModel]) -> None:
        stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by: dict) -> None:
        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        ).returning(self.model.id)
        await self.check_object_not_found(stmt)

    async def delete(self, **filter_by: dict) -> None:
        stmt = sqlalchemy.delete(self.model).filter_by(**filter_by).returning(self.model.id)
        await self.check_object_not_found(stmt)

        await self.session.execute(stmt)

    async def check_object_not_found(self, stmt) -> None:
        if (await self.session.execute(stmt)).first() is None:
            raise ObjectNotFoundException
