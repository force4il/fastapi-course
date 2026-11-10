import json
from unittest import mock
from typing import AsyncGenerator

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

import pytest
from httpx import ASGITransport, AsyncClient
from contextlib import asynccontextmanager

from src.api.dependecies import get_db
from src.config import settings
from src.database import Base, async_session_maker_null_pool, engine_null_pool
from src.main import app
from src.models import *
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool():
    async with DBManager(async_session_maker_null_pool) as db:
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


def get_json_user_data() -> dict:
    return {
        "email": "test@test.com",
        "password": "1234",
        "first_name": "test",
        "last_name": "test",
    }


@asynccontextmanager
async def make_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
async def db() -> AsyncGenerator:
    async for db in get_db_null_pool():
        yield db


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open("tests/mock_hotels.json", encoding="utf-8") as file:
        hotels = json.load(file)
    with open("tests/mock_rooms.json", encoding="utf-8") as file:
        rooms = json.load(file)

    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels]
    rooms = [RoomAdd.model_validate(room) for room in rooms]

    async with DBManager(async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotels)
        await db_.rooms.add_bulk(rooms)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator:
    async with make_client() as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    response = await ac.post(
        url="/auth/register",
        json=get_json_user_data(),
    )
    assert response.status_code == 200


@pytest.fixture(scope="session", autouse=True)
async def auth_ac(register_user) -> AsyncGenerator:
    async with make_client() as client:
        response = await client.post(
            url="/auth/login",
            json=get_json_user_data(),
        )
        assert response.status_code == 200
        assert response.cookies["access_token"]
        yield client
