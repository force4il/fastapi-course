from datetime import date

from api.dependecies import PaginationId
from src.exceptions import (
    ObjectNotFoundException,
    RoomNotFoundException,
    check_date_to_after_date_from,
)
from schemas.facilities import RoomFacilityAdd
from schemas.rooms import BaseRoom, RoomAdd, RoomPatch, RoomPatchRequest
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def get_rooms(
        self,
        hotel_id: PaginationId,
        date_from: date,
        date_to: date,
    ):
        check_date_to_after_date_from(date_from=date_from, date_to=date_to)
        return await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )

    async def get_room(self, room_id: PaginationId, hotel_id: PaginationId):
        return await self.db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)

    async def create_room(self, hotel_id: PaginationId, room_data: BaseRoom):
        await HotelService(self.db).check_hotel_exists(hotel_id)

        room_add_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room = await self.db.rooms.add(room_add_data)
        rooms_facilities_data = [
            RoomFacilityAdd(room_id=room.id, facility_id=facility_id)
            for facility_id in room_data.facilities_ids
        ]
        await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()

    async def edit_room(
        self, hotel_id: PaginationId, room_id: PaginationId, room_data: BaseRoom
    ) -> None:
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.get_room(hotel_id=hotel_id, room_id=room_id)

        room_edit_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        try:
            await self.db.rooms.edit(room_edit_data, id=room_id, hotel_id=hotel_id)
            await self.db.rooms_facilities.set_room_facility(room_id, room_data.facilities_ids)
            await self.db.commit()
        except ObjectNotFoundException:
            raise RoomNotFoundException

    async def part_edit_room(
        self,
        hotel_id: PaginationId,
        room_id: PaginationId,
        room_data: RoomPatchRequest,
    ) -> None:
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.get_room(hotel_id=hotel_id, room_id=room_id)

        room_patch_dict = room_data.model_dump(exclude_unset=True)
        room_patch_data = RoomPatch(hotel_id=hotel_id, **room_patch_dict)
        try:
            await self.db.rooms.edit(
                room_patch_data, exclude_unset=True, id=room_id, hotel_id=hotel_id
            )
            if "facilities_ids" in room_patch_dict:
                await self.db.rooms_facilities.set_room_facility(
                    room_id, room_patch_dict["facilities_ids"]
                )
            await self.db.commit()
        except ObjectNotFoundException:
            RoomNotFoundException

    async def delete_room(self, hotel_id: PaginationId, room_id: PaginationId) -> None:
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.get_room(hotel_id=hotel_id, room_id=room_id)
        try:
            await self.db.rooms.delete(id=room_id, hotel_id=hotel_id)
            await self.db.commit()
        except ObjectNotFoundException:
            raise RoomNotFoundException
