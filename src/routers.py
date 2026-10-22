from fastapi import APIRouter

from src.api.auth import router as router_auth
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.api.hotels import router as router_hotels
from src.api.images import router as router_images
from src.api.rooms import router as router_rooms

main_router = APIRouter()

main_router.include_router(router_auth)
main_router.include_router(router_hotels)
main_router.include_router(router_rooms)
main_router.include_router(router_bookings)
main_router.include_router(router_facilities)
main_router.include_router(router_images)
