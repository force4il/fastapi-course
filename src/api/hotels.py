from datetime import date

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from src.api.dependecies import DBDep, PaginationDep, PaginationId
from src.schemas.hotels import HotelAdd, HotelPatch

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get(
    "",
    description="Список отелей, совпадающих с введенными данными",
    summary="получение отелей по id или title",
)
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    location: str | None = Query(None, description="Адрес отеля"),
    title: str | None = Query(None, description="Название отеля"),
    date_from: date = Query(example="2026-08-01"),
    date_to: date = Query(example="2026-08-10"),
):
    per_page = pagination.per_page or 5
    return await db.hotels.get_filterd_by_time(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
    )


@router.get("/{hotel_id}", summary="получение отеля по id")
async def get_hotel(db: DBDep, hotel_id: PaginationId):
    return await db.hotels.get_one_or_none(id=hotel_id)


@router.post("", summary="добавление отеля")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {"title": "Отель Сочи", "location": "ул. Красная поляна, 2"},
            },
            "2": {
                "summary": "ДУбай",
                "value": {
                    "title": "Отель Дубай возле моря",
                    "location": "ул. Шанхайская, 10",
                },
            },
        }
    ),
):
    hotel = await db.hotels.add(hotel_data)
    await db.commit()

    # print(add_hotel_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}", summary="полное изменение отеля через фильтр")
async def put_hotel(db: DBDep, hotel_id: PaginationId, hotel_data: HotelAdd) -> dict:
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}", summary="Частичное обновление данных (или также полное) об отеле"
)
async def patch_hotel(
    db: DBDep, hotel_id: PaginationId, hotel_data: HotelPatch
) -> dict:
    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}", summary="удаление отеля из бд через фильтр")
async def delete_hotel(db: DBDep, hotel_id: PaginationId) -> dict:
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}
