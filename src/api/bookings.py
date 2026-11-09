from fastapi import APIRouter, HTTPException

from exceptions import AllRoomsAreBookedException, ObjectNotFoundException
from schemas.rooms import Room
from src.api.dependecies import DBDep, UserIdDep
from src.schemas.bookings import BookingAdd, BookingRequest

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("", summary="Получение всех бронирований")
async def get_all_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.get("/me", summary="Получение только своих бронирований")
async def get_my_bookings(db: DBDep, user_id: UserIdDep):
    return await db.bookings.get_filtered(user_id=user_id)


@router.post("", summary="Добавление бронирования")
async def add_booking(db: DBDep, booking_data: BookingRequest, user_id: UserIdDep):
    try:
        room: Room = await db.rooms.get_one(id=booking_data.room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=400, detail="Номер не найден")

    booking_add_data = BookingAdd(**booking_data.model_dump(), user_id=user_id, price=room.price)
    try:
        booking = await db.bookings.add_booking(booking_add_data, hotel_id=room.hotel_id)
    except AllRoomsAreBookedException as err:
        raise HTTPException(status_code=409, detail=err.detail)

    await db.commit()

    return {"status": "OK", "data": booking}


@router.delete("/{booking_id}", summary="Удаление бронирования")
async def delete_booking(db: DBDep, booking_id: int) -> dict:
    await db.bookings.delete(id=booking_id)
    await db.commit()
    return {"status": "OK"}
