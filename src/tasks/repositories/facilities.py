from sqlalchemy import delete, insert, select

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from tasks.repositories.base import BaseRepository
from tasks.repositories.mappers.mappers import FacilityDataMapper


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilityDataMapper


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm
    mapper = FacilityDataMapper

    async def set_room_facility(self, room_id: int, facilities_ids: list[int]):
        cur_fac_ids = select(self.model.facility_id).filter_by(room_id=room_id)
        result = await self.session.execute(cur_fac_ids)
        current_facilities_ids: list[int] = result.scalars().all()
        ids_to_del: list[int] = list(set(current_facilities_ids) - set(facilities_ids))
        ids_to_ins: list[int] = list(set(facilities_ids) - set(current_facilities_ids))

        if ids_to_del:
            del_m2m_fac_stmt = delete(self.model).filter(
                self.model.room_id == room_id, self.model.facility_id.in_(ids_to_del)
            )
            await self.session.execute(del_m2m_fac_stmt)

        if ids_to_ins:
            ins_m2m_fac_stmt = insert(self.model).values(
                [{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_ins]
            )
            await self.session.execute(ins_m2m_fac_stmt)
