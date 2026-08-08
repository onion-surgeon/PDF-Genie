from fastapi import FastAPI
from app.routers import api_router
from app.routers.telegram import telegram_router 
from app.core.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title = "PDF-Genie",
    description="A backend oriented project to answer questions related to the uploaded PDFs",
    )


app.include_router(api_router)
