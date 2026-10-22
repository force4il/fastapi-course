import sys
from contextlib import asynccontextmanager
from pathlib import Path

# import asyncio

sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.init import redis_manager
from src.routers import main_router

# from src.api.dependecies import get_db


# async def send_emails_bookings_today_checkin():
#     async for db in get_db():
#         bookings = await db.bookings.get_bookings_checkin_today()
#         print(bookings)


# async def run_send_emails_forever():
#     while True:
#         await send_emails_bookings_today_checkin()
#         await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # asyncio.create_task(run_send_emails_forever())
    await redis_manager.connect()

    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
