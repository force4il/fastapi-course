from repositories.bookings import BookingsRepository
from repositories.facilities import FacilitiesRepository, RoomsFacilitiesRepository
from repositories.hotels import HotelsRepository
from repositories.rooms import RoomsRepository
from repositories.users import UsersRepository


class DBManager:

    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> "DBManager":
        self.session = self.session_factory()

        self.hotels = HotelsRepository(self.session)
        self.users = UsersRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        self.rooms_facilities = RoomsFacilitiesRepository(self.session)

        return self

    async def __aexit__(self, *args) -> None:
        await self.session.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()
