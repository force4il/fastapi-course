from datetime import date

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from services.hotels import HotelService
from src.exceptions import (
    HotelNotFoundException,
    ObjectNotFoundException,
    HotelNotFoundHTTPException,
)
from src.api.dependecies import DBDep, PaginationDep, PaginationId
from src.schemas.hotels import HotelAdd, HotelPatch

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get(
    "",
    description="Список отелей",
    summary="получение отелей",
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
    hotels = await HotelService(db).get_filtered_by_time(
        pagination=pagination, location=location, title=title, date_from=date_from, date_to=date_to
    )
    return {"status": "OK", "data": hotels}


@router.get("/{hotel_id}", summary="получение отеля")
async def get_hotel(db: DBDep, hotel_id: PaginationId):
    try:
        return await HotelService(db).get_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException


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
    hotel = await HotelService(db).create_hotel(hotel_data)
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}", summary="полное изменение отеля через фильтр")
async def put_hotel(db: DBDep, hotel_id: PaginationId, hotel_data: HotelAdd) -> dict:
    try:
        await HotelService(db).put_hotel(hotel_id=hotel_id, hotel_data=hotel_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK"}


@router.patch("/{hotel_id}", summary="Частичное обновление данных (или также полное) об отеле")
async def patch_hotel(db: DBDep, hotel_id: PaginationId, hotel_data: HotelPatch) -> dict:
    try:
        await HotelService(db).patch_hotel(hotel_id=hotel_id, hotel_data=hotel_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK"}


@router.delete("/{hotel_id}", summary="удаление отеля")
async def delete_hotel(db: DBDep, hotel_id: PaginationId) -> dict:
    try:
        await HotelService(db).delete_hotel(hotel_id=hotel_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException

    return {"status": "OK"}
