import logging

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.exceptions.types import FileTypeError, TelegramAPIError
from app.services.pdf_service import PDFService
from app.services.telegram_api import send_message
from app.services.telegram_service import TelegramWebhookDispatcher
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

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
    try:

        update = await request.json()

        message = update.get("message", {})
        chat_id = update["message"]["chat"]["id"]

        await dispatcher.dispatch(
            update=update,
            db=db,
            pdf_service=pdf_service,
            user_service=user_service,
        )

        return {"ok": True}

    except FileTypeError as e:
        logger.warning(f"Invalid file type from chat {chat_id}: {e}")
        await send_message(chat_id, str(e))
    except IntegrityError as e:
        logger.warning(f"Duplicate PDF from chat {chat_id}: {e}")
        await send_message(chat_id, "File already exists")
    except TelegramAPIError as e:
        logger.error(f"Telegram API error for chat {chat_id}: {e}", exc_info=True)
        await send_message(chat_id, str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing webhook for chat {chat_id}: {e}", exc_info=True)
        await send_message(chat_id, "Operation failed")

    return {"ok": True}
