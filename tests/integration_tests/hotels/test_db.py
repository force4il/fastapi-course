from src.schemas.hotels import HotelAdd
from src.utils.db_manager import DBManager
from src.database import async_session_maker


async def test_add_hotel():
    hotel_data = HotelAdd(title="Hotel1", location="Paris")
    async with DBManager(async_session_maker) as db:
        new_hotel_data = await db.hotels.add(hotel_data)
        await db.commit()

    