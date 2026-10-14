from datetime import date

from fastapi import APIRouter, Body, Query

from src.api.dependecies import DBDep, PaginationId
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import BaseRoom, RoomAdd, RoomPatch, RoomPatchRequest

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms", summary="Получение номеров отеля")
async def get_rooms(
    db: DBDep,
    hotel_id: PaginationId,
    date_from: date = Query(example="2026-08-01"),
    date_to: date = Query(example="2026-08-10"),
):
    return await db.rooms.get_filtered_by_time(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )


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
):
    room_add_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(room_add_data)
    rooms_facilities_data = [
        RoomFacilityAdd(room_id=room.id, facility_id=facility_id)
        for facility_id in room_data.facilities_ids
    ]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()

    return {"status": "OK", "data": room}


@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение номера отеля")
async def get_room(db: DBDep, hotel_id: PaginationId, room_id: PaginationId):
    return await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)


@router.put("/{hotel_id}/rooms/{room_id}", summary="Полное изменение номера отеля")
async def edit_room(
    db: DBDep, hotel_id: PaginationId, room_id: PaginationId, room_data: BaseRoom
) -> dict:
    room_edit_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(room_edit_data, id=room_id, hotel_id=hotel_id)
    await db.rooms_facilities.set_room_facility(room_id, room_data.facilities_ids)
    await db.commit()

    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}", summary="Частичное изменение номера отеля")
async def part_edit_room(
    db: DBDep,
    hotel_id: PaginationId,
    room_id: PaginationId,
    room_data: RoomPatchRequest,
) -> dict:
    room_patch_dict = room_data.model_dump(exclude_unset=True)
    room_patch_data = RoomPatch(hotel_id=hotel_id, **room_patch_dict)
    await db.rooms.edit(
        room_patch_data, exclude_unset=True, id=room_id, hotel_id=hotel_id
    )
    if "facilities_ids" in room_patch_dict:
        await db.rooms_facilities.set_room_facility(
            room_id, room_patch_dict["facilities_ids"]
        )
    await db.commit()

    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}", summary="Удаление номера отеля")
async def get_room(db: DBDep, hotel_id: PaginationId, room_id: PaginationId) -> dict:
    await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    await db.commit()
    return {"status": "OK"}
