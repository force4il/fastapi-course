import pytest

from tests.conftest import get_db_null_pool


@pytest.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null_pool():
        await _db.bookings.delete()
        await _db.commit()


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, "2025-08-01", "2025-08-10", 200),
        (1, "2025-08-02", "2025-08-11", 200),
        (1, "2025-08-03", "2025-08-12", 200),
        (1, "2025-08-04", "2025-08-13", 200),
        (1, "2025-08-05", "2025-08-14", 200),
        (1, "2025-08-06", "2025-08-15", 409),
        (1, "2025-08-17", "2025-08-20", 200),
    ],
)
async def test_booking_crud(room_id, date_from, date_to, status_code, auth_ac):
    # room_id = (await db.rooms.get_all())[0].id
    response = await auth_ac.post(
        "/bookings",
        json={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )

    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert "data" in res
        assert res["status"] == "OK"


@pytest.mark.parametrize(
    "room_id, date_from, date_to, bookings_count",
    [
        (1, "2025-08-01", "2025-08-10", 1),
        (1, "2025-08-02", "2025-08-11", 2),
        (1, "2025-08-03", "2025-08-12", 3),
    ],
)
async def test_add_and_get_my_bookings(
    room_id, date_from, date_to, bookings_count, auth_ac, delete_all_bookings
):
    response = await auth_ac.post(
        "/bookings",
        json={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == 200

    response_me = await auth_ac.get("/bookings/me")
    assert response_me.status_code == 200
    assert len(response_me.json()) == bookings_count
