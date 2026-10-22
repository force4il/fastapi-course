from fastapi import APIRouter, Body, HTTPException, Response
from sqlalchemy.exc import IntegrityError

from src.api.dependecies import DBDep, UserIdDep
from src.schemas.users import UserAdd, UserRequestAdd, UserWithHashPass
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутенфикация"])


@router.post("/login", summary="аутентификация пользователя")
async def login_user(
    db: DBDep,
    response: Response,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "User1",
                "value": {
                    "email": "test20@gmail.com",
                    "password": "1234",
                    "first_name": "Denis",
                    "last_name": "Bogdanov",
                },
            },
            "2": {
                "summary": "User2",
                "value": {
                    "email": "realemail@yandex.ru",
                    "password": "querty",
                    "first_name": "BOris",
                    "last_name": "Britva",
                },
            },
        }
    ),
) -> dict:
    user: UserWithHashPass = await db.users.get_user_with_hashed_pass(email=data.email)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Пользователь с таким email не зарегестрирован"
        )
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный пароль")

    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)

    return {"access_token": access_token}


@router.post("/register", summary="регистрация пользователя и добавление данных в бд")
async def register_user(
    db: DBDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "User1",
                "value": {
                    "email": "test20@gmail.com",
                    "password": "1234",
                    "first_name": "Denis",
                    "last_name": "Bogdanov",
                },
            },
            "2": {
                "summary": "User2",
                "value": {
                    "email": "realemail@yandex.ru",
                    "password": "querty",
                    "first_name": "BOris",
                    "last_name": "Britva",
                },
            },
        }
    ),
) -> dict:
    hashed_password = AuthService().hash_password(data.password)
    hashed_user_data = UserAdd(
        email=data.email,
        hashed_password=hashed_password,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    try:
        await db.users.add(hashed_user_data)
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=403, detail="Пользователь с такой почтой уже существует"
        )

    return {"status": "OK"}


@router.post("/logout", summary="Выход из системы")
def logout_user(response: Response) -> dict:
    response.delete_cookie("access_token")
    return {"status": "Успешный выход из системы"}


@router.get("/me", summary="получение данных о текущем пользователе")
async def get_me(db: DBDep, user_id: UserIdDep):
    return await db.users.get_one_or_none(id=user_id)
