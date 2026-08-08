import httpx, logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.pdf import PDF
from app.models.users import User
from app.services.pdf_service import PDFService
from app.services.telegram_api import download_file_telegram, send_message
from app.services.user_service import UserService
from app.workers.tasks import chunk_embed_pipeline, output_orchestrator_task
from app.exceptions.types import *

logger = logging.getLogger(__name__)

class TelegramWebhookDispatcher:
    async def dispatch(self, update: dict, db: AsyncSession, pdf_service: PDFService, 
        user_service: UserService, ) -> None:

        
        message = update.get("message", {})
        chat_id = update["message"]["chat"]["id"]
        t_id = message["from"]["id"]
        document = message.get("document")

        if document:
            await self.handle_document(
                chat_id=chat_id,
                t_id=t_id,
                document=document,
                db=db,
                pdf_service=pdf_service,
            )
            return

        if text := message.get("text"):
            await self.handle_text(
                chat_id=chat_id,
                t_id=t_id,
                text=text,
                db=db,
                user_service=user_service,
            )

    async def handle_text(self, chat_id: int, t_id: int, text: str, db: AsyncSession,
        user_service: UserService) -> None:
        user_id = await user_service.get_user_id_from_telegram_id(db, t_id)

        if not await user_service.check_user_pdf_exists(db, user_id):
            await send_message(chat_id, "Upload a document first")
        else:
            output_orchestrator_task.delay(chat_id, user_id, text)
            

    async def handle_document(self, chat_id: int, t_id: int, document: dict, db: AsyncSession, 
        pdf_service: PDFService, ) -> None:

        file_id = document["file_id"]
        file_name = document.get("file_name")
        mime_type = document.get("mime_type")

        if mime_type != "application/pdf":
            raise FileTypeError(mime_type) 

        file_bytes = await download_file_telegram(file_id)

        try:
            userid = await check_telegram_user_exists(db, t_id)

            if not userid:
                userid = await create_telegram_user(db, t_id)

            pdf_id = await pdf_service.write_pdf(
                db,
                file_bytes,
                file_name,
                userid
            )
            notify_user_safe(chat_id, "File upload started")
            chunk_embed_pipeline.delay(pdf_id, chat_id)

        except Exception as e:
            raise e
            

async def check_telegram_user_exists(db: AsyncSession, t_id : int) -> int | None :
    query = select(User).where(User.telegram_id == t_id)
    result = await db.execute(query)
    user = result.scalars().first()
    return user.userid if user else None


async def create_telegram_user(db:AsyncSession,t_id: int) -> int:
    user = User(
        telegram_id = t_id
    )
    db.add(user)
    await db.commit()
    return user.userid

async def check_user_pdf_exists(db: AssertionError,user_id:int):
    query = select(PDF).where(PDF.userid == user_id)
    id = await db.execute(query)
    return id.scalars().first()

async def notify_user_safe(chat_id: int, text: str):
    try:
        await send_message(chat_id, text)
    except Exception as e:
        logger.error(f"Failed to notify chat {chat_id}: {e}", exc_info=True)
