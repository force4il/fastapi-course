from src.models.bookings import BookingsOrm
from repositories.base import BaseRepository
from repositories.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper
