from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.services.pdf_service import PDFService
from app.services.telegram_service import TelegramWebhookDispatcher
from app.services.user_service import UserService

telegram_router = APIRouter()


@telegram_router.post("/webhook")
async def telegram_webhook(
    request: Request,
    dispatcher: Annotated[
        TelegramWebhookDispatcher,
        Depends(TelegramWebhookDispatcher),
    ],
    pdf_service: Annotated[PDFService, Depends(PDFService)],
    user_service: Annotated[UserService, Depends(UserService)],
    db: AsyncSession = Depends(get_db),
):
    update = await request.json()

    await dispatcher.dispatch(
        update=update,
        db=db,
        pdf_service=pdf_service,
        user_service=user_service,
    )

    return {"ok": True}

