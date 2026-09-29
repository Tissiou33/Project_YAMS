from fastapi import APIRouter

from app.api.v1 import admin, auth, deliveries, geo, orders, shops

api_router = APIRouter()
for module in (auth, geo, shops, orders, deliveries, admin):
    api_router.include_router(module.router)
