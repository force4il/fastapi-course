from datetime import date

from fastapi import APIRouter, Body, Query

from services.rooms import RoomService
from src.exceptions import (
    HotelNotFoundException,
    RoomNotFoundException,
    HotelNotFoundHTTPException,
    RoomNotFoundHTTPException,
)
from src.api.dependecies import DBDep, PaginationId
from src.schemas.rooms import BaseRoom, RoomPatchRequest

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms", summary="Получение номеров отеля")
async def get_rooms(
    db: DBDep,
    hotel_id: PaginationId,
    date_from: date = Query(example="2026-08-01"),
    date_to: date = Query(example="2026-08-10"),
):
    return await RoomService(db).get_rooms(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение номера отеля")
async def get_room(db: DBDep, hotel_id: PaginationId, room_id: PaginationId):
    try:
        room = await RoomService(db).get_room(room_id=room_id, hotel_id=hotel_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

    return room


@router.post("/{hotel_id}/rooms", summary="Добавление номера для отеля")
async def create_room(
    db: DBDep,
    hotel_id: PaginationId,
    room_data: BaseRoom = Body(
        openapi_examples={
            "1": {
                "summary": "Комната 1",
                "value": {
                    "title": "VIP room",
                    "description": "Номер с бильярдом, сауной, баней и джакузи",
                    "price": 10000,
                    "quantity": 5,
                    "facilities_ids": [],
                },
            },
            "2": {
                "summary": "Комната 2",
                "value": {
                    "title": "Rich Room",
                    "description": "Номер с видом на море",
                    "price": 8000,
                    "quantity": 10,
                    "facilities_ids": [],
                },
            },
        }
    ),
) -> dict:
    try:
        room = await RoomService(db).create_room(hotel_id=hotel_id, room_data=room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}", summary="Полное изменение номера отеля")
async def edit_room(
    db: DBDep, hotel_id: PaginationId, room_id: PaginationId, room_data: BaseRoom
) -> dict:
    try:
        await RoomService(db).edit_room(hotel_id=hotel_id, room_id=room_id, room_data=room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}", summary="Частичное изменение номера отеля")
async def part_edit_room(
    db: DBDep,
    hotel_id: PaginationId,
    room_id: PaginationId,
    room_data: RoomPatchRequest,
) -> dict:
    try:
        await RoomService(db).part_edit_room(
            hotel_id=hotel_id, room_id=room_id, room_data=room_data
        )
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}", summary="Удаление номера отеля")
async def delete_room(db: DBDep, hotel_id: PaginationId, room_id: PaginationId) -> dict:
    try:
        RoomService(db).delete_room(hotel_id=hotel_id, room_id=room_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

    return {"status": "OK"}
