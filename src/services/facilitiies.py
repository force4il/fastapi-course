from schemas.facilities import FacilityAdd
from src.services.base import BaseService
from tasks.tasks import test_task


class FacilityService(BaseService):

    async def create_facility(self, facility_data: FacilityAdd):
        facility = await self.db.facilities.add(facility_data)
        await self.db.commit()

        test_task.delay()

        return facility