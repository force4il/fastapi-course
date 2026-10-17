from datetime import date

from sqlalchemy import select

from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from repositories.base import BaseRepository
from repositories.mappers.mappers import HotelDataMapper
from repositories.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper

    async def get_filterd_by_time(
        self,
        date_from: date,
        date_to: date,
        location: str | None,
        title: str | None,
        limit: int,
        offset: int,
    ) -> list[Hotel]:
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to)
        hotels_ids = select(RoomsOrm.hotel_id).filter(RoomsOrm.id.in_(rooms_ids_to_get))
        if title:
            hotels_ids = hotels_ids.filter(HotelsOrm.title.ilike(f"%{title.strip()}%"))
        if location:
            hotels_ids = hotels_ids.filter(
                HotelsOrm.location.ilike(f"%{location.strip()}%")
            )

        hotels_ids = hotels_ids.limit(limit).offset(offset)

        return await self.get_filtered(HotelsOrm.id.in_(hotels_ids))
