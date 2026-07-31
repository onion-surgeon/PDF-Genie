from fastapi import FastAPI
from app.routers import api_router


app = FastAPI(
    title = "PDF-Genie",
    description="A backend oriented project to answer questions related to the uploaded PDFs",
    )


app.include_router(api_router)
