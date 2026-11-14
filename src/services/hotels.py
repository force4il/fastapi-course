from datetime import date

from fastapi import Query

from api.dependecies import PaginationDep, PaginationId
from src.exceptions import (
    HotelNotFoundException,
    ObjectNotFoundException,
    check_date_to_after_date_from,
)
from schemas.hotels import HotelAdd
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_filtered_by_time(
        self,
        pagination: PaginationDep,
        location: str | None = Query(None, description="Адрес отеля"),
        title: str | None = Query(None, description="Название отеля"),
        date_from: date = Query(example="2026-08-01"),
        date_to: date = Query(example="2026-08-10"),
    ):
        check_date_to_after_date_from(date_from=date_from, date_to=date_to)

        per_page = pagination.per_page or 5
        return await self.db.hotels.get_filterd_by_time(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )

    async def get_hotel(self, hotel_id: PaginationId):
        return await self.db.hotels.get_one(id=hotel_id)

    async def create_hotel(self, hotel_data: HotelAdd):
        hotel = await self.db.hotels.add(hotel_data)
        await self.db.commit()

        return hotel

    async def put_hotel(self, hotel_id: PaginationId, hotel_data: HotelAdd):
        try:
            await self.db.hotels.edit(hotel_data, id=hotel_id)
            await self.db.commit()
        except ObjectNotFoundException:
            raise HotelNotFoundException

    async def patch_hotel(self, hotel_id: PaginationId, hotel_data: HotelAdd):
        try:
            await self.db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
            await self.db.commit()
        except ObjectNotFoundException:
            raise HotelNotFoundException

    async def delete_hotel(self, hotel_id: PaginationId):
        try:
            await self.db.hotels.delete(id=hotel_id)
            await self.db.commit()
        except ObjectNotFoundException:
            raise HotelNotFoundException

    async def check_hotel_exists(self, hotel_id: PaginationId):
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException