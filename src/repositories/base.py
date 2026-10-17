import sqlalchemy
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import insert, select, update

from repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session) -> None:
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)

        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_all(self, *args: tuple, **kwargs: dict) -> list:
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by: dict):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None

        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(stmt)
        model = result.scalars().one()

        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]) -> None:
        stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(stmt)

    async def edit(
        self, data: BaseModel, exclude_unset: bool = False, **filter_by: dict
    ) -> None:
        await self.check_one_item(**filter_by)

        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(stmt)

    async def delete(self, **filter_by: dict) -> None:
        await self.check_one_item(**filter_by)

        stmt = sqlalchemy.delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)

    async def check_one_item(self, **filter_by: dict) -> None:
        try:
            result = await self.get_one_or_none(**filter_by)
            if result is None:
                raise HTTPException(404, detail="Удаляемый объект не найден")
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise HTTPException(
                400, detail="По заданному фильтру найдено больше 1 объекта"
            )
