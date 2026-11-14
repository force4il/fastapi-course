from datetime import date

from src.schemas.bookings import BookingAdd


async def test_bookings_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2024, month=8, day=24),
        date_to=date(year=2025, month=9, day=10),
        price=100,
    )

    add_booking = await db.bookings.add(booking_data)

    booking = await db.bookings.get_one_or_none(id=add_booking.id)
    assert booking
    assert booking.id == add_booking.id
    assert booking.room_id == add_booking.room_id

    updated_date_from = date(year=2025, month=8, day=24)
    updated_date_to = date(year=2026, month=8, day=24)
    updated_price = 1000
    update_booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=updated_date_from,
        date_to=updated_date_to,
        price=updated_price,
    )
    await db.bookings.edit(update_booking_data, id=booking.id)
    update_booking = await db.bookings.get_one_or_none(id=booking.id)
    assert update_booking
    assert update_booking.id == add_booking.id
    assert update_booking.date_from == updated_date_from
    assert update_booking.date_to == updated_date_to
    assert update_booking.price == updated_price

    await db.bookings.delete(id=booking.id)
    booking_after_delete = await db.bookings.get_one_or_none(id=booking.id)
    assert booking_after_delete is None
