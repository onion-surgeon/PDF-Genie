from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db  
from app.models.pdf import PDF, Status
from fastapi import Depends

from app.services.pdf_service import PDFService

telegram_router = APIRouter()


@telegram_router.post("/upload")
async def upload_pdf(
    pdf_service: Annotated[PDFService, Depends(PDFService)],
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        await pdf_service.write_pdf(db, file)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="This PDF has already been uploaded")
    

    return "File uploaded"
