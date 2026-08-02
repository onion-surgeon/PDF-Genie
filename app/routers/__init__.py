from app.routers.telegram import telegram_router 
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(telegram_router, prefix= "/telegram")

