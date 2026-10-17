from time import sleep
from PIL import Image
from pathlib import Path
import asyncio

from src.tasks.celery_app import celery_instance
from src.api.dependecies import DBManager
from src.database import async_session_maker

@celery_instance.task
def test_task():
    sleep(5)
    print("Its done")


@celery_instance.task
def resize_image(image_path: str):
    sizes = [i for i in range(1000, 10000, 1000)]
    output_folder = "src/static/images/"

    img = Image.open(image_path)
    filename = Path(image_path).name
    ext = Path(image_path).suffix

    for size in sizes:
        img_resized = img.resize((size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS)
        new_filename = f"{filename}_{size}px{ext}"
        output_path = Path(output_folder) / new_filename

        img_resized.save(output_path.absolute())


async def get_bookings_with_today_checkin():
    async with DBManager(async_session_maker) as db:
        bookings = await db.bookings.get_bookings_checkin_today()


@celery_instance.task(name="booking_today_checkin")
def send_emails_to_users_checkin():
    asyncio.run(get_bookings_with_today_checkin())