from src.models.bookings import BookingsOrm
from tasks.repositories.base import BaseRepository
from tasks.repositories.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper
