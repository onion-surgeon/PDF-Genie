import uuid as uuid_lib
import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.pdf import PDF, Status
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.document_loaders import PyMuPDFLoader


class PDFService:

    def __init__(self):
        pass

    async def write_pdf(self, db: AsyncSession, file: bytes, filename: str, user_id: int):
        file_uuid = uuid_lib.uuid4()
        folder_path = settings.UPLOAD_DIR / str(file_uuid)
        storage_path = folder_path / filename
        contents = file
        content_sha256 = hashlib.sha256(contents).hexdigest()
        new_pdf = PDF(
            pdfname=filename,
            uuid=file_uuid,
            content_sha256=content_sha256,
            storage_path=str(storage_path),
            status=Status.UPLOADED,
            userid = user_id
        )

        try:
            db.add(new_pdf)
            await db.commit()
            await db.refresh(new_pdf)

            folder_path.mkdir(parents=True, exist_ok=True)
            with open(storage_path, "wb") as f:
                f.write(contents)

        except IntegrityError as e:
            await db.rollback()
            raise e
        
        except Exception as e:
            await db.rollback()

            if storage_path.exists():
                storage_path.unlink()    
            raise e

        
        return new_pdf.pdfid

    async def load_pdf(self,db:AsyncSession,pdf_id) -> PDF:
        query = select(PDF).where(PDF.pdfid == pdf_id)
        result = await db.execute(query)
        return result.scalars().first()
    
