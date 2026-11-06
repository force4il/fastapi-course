from datetime import date

from sqlalchemy import select

from exceptions import AllRoomsAreBookedException
from repositories.utils import rooms_ids_for_booking
from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper
from src.schemas.bookings import BookingAdd


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings_checkin_today(self):
        query = select(self.model).filter(self.model.date_from == date.today())

        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in result.scalars().all()]

    async def add_booking(self, data: BookingAdd, hotel_id: int):
        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=data.date_from, date_to=data.date_to, hotel_id=hotel_id
        )
        rooms_ids_to_book_res = await self.session.execute(rooms_ids_to_get)
        rooms_ids_to_book: list[int] = rooms_ids_to_book_res.scalars().all()

        if data.room_id in rooms_ids_to_book:
            return await self.add(data)

        raise AllRoomsAreBookedException
