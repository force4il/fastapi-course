from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependecies import DBDep
from src.schemas.facilities import FacilityAdd
from src.tasks.tasks import test_task

router = APIRouter(prefix="/facilities", tags=["Удобства и услуги"])


@router.get("", summary="Получение всех удобств")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post("", summary="Добавление новой услуги")
async def add_facility(
    db: DBDep,
    facility_data: FacilityAdd = Body(
        openapi_examples={
            "1": {"summary": "Услуга 1", "value": {"title": "Кондиционер"}},
            "2": {"summary": "Услуга 2", "value": {"title": "Холодильник с пивком"}},
        }
    ),
):
    facility = await db.facilities.add(facility_data)
    await db.commit()

    test_task.delay()

    return {"status": "OK", "data": facility}


@router.delete("/{facility_id}", summary="Удаление удобства")
async def delete_facility(facility_id: int, db: DBDep) -> dict:
    await db.facilities.delete(id=facility_id)
    await db.commit()
    return {"status": "OK"}
