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

    async def write_pdf(self, db: AsyncSession, file: bytes):
        file_uuid = uuid_lib.uuid4()
        folder_path = settings.UPLOAD_DIR / str(file_uuid)
        storage_path = folder_path / file.filename
        contents = await file.read()
        content_sha256 = hashlib.sha256(contents).hexdigest()
        new_pdf = PDF(
            pdfname=file.filename,
            uuid=file_uuid,
            content_sha256=content_sha256,
            storage_path=str(storage_path),
            status=Status.UPLOADED,
        )

        try:
            db.add(new_pdf)
            await db.commit()
            await db.refresh(new_pdf)
        except IntegrityError as e:
            await db.rollback()
            raise e

        folder_path.mkdir(parents=True, exist_ok=True)
        with open(storage_path, "wb") as f:
            f.write(contents)

        
        return True

    async def load_pdf(self,db:AsyncSession,pdf_id):
        query = select(PDF).where(PDF.pdfid == pdf_id)
        result = await db.exectue(query)
        return result.scalars().first()
    
