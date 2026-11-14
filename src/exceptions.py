from datetime import date

from fastapi import HTTPException


class NabronirovalException(Exception):
    detail = "Someone error"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(NabronirovalException):
    detail = "Сущность не найдена"


class AllRoomsAreBookedException(NabronirovalException):
    detail = "Все номера уже забронированы"


class ObjectAlreadyExistsException(NabronirovalException):
    detail = "Объект уже существует"


class RoomNotFoundException(ObjectNotFoundException):
    detail = "Такого номера не существует"


class HotelNotFoundException(ObjectNotFoundException):
    detail = "Такого отеля не существует"


def check_date_to_after_date_from(date_to: date, date_from: date):
    if date_to <= date_from:
        raise HTTPException(status_code=422, detail="Дата заезда позже, чем дата выезда")


class NabronirovalHTTPException(HTTPException):
    status_code = 400
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundHTTPException(NabronirovalHTTPException):
    status_code = 404
    detail = "Отель не найден"


class RoomNotFoundHTTPException(NabronirovalHTTPException):
    status_code = 404
    detail = "Номер не найден"
