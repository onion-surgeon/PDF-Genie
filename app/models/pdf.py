from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Boolean, Uuid, DateTime, String, Enum as SQEnum, func
from datetime import datetime
from enum import Enum

from app.core.db.base import Base

class Status(str, Enum):
    UPLOADED = 'uploaded'
    PROCESSING = 'processing'
    CHUNKED = 'chunked'
    EMBEDDED = 'embedded'
    FAILED = 'failed'
    
class PDF(Base):
    __tablename__ = "pdfs"
    pdfid: Mapped[int] = mapped_column(Integer, primary_key=True, index= True)
    pdfname: Mapped[str] = mapped_column(String, nullable= False,)
    uuid: Mapped[str] = mapped_column(Uuid, nullable= False, unique= True)
    storage_path: Mapped[str] = mapped_column(String, nullable= False)
    status: Mapped[Status] = mapped_column(SQEnum(Status), nullable= False, index= True)
    failure_reason: Mapped[str] = mapped_column(String, nullable= True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable= False, server_default= func.now())
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable= False, server_default= func.now(), onupdate= func.now())

