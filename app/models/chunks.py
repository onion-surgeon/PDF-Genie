from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, DateTime, String, Enum as SQEnum, func, ForeignKey
from app.core.db.base import Base
from pgvector.sqlalchemy import Vector
from datetime import datetime
from enum import Enum

class ChunkStatus(str, Enum):
    PENDING = 'pending'
    EMBEDDED = 'embedded'
    FAILED = 'failed'

class Chunk(Base):
    __tablename__ = "chunks"

    chunkid: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pdfid: Mapped[int] = mapped_column(Integer, ForeignKey("pdfs.pdfid"), index=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ChunkStatus] = mapped_column(SQEnum(ChunkStatus), nullable=False, index=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    section: Mapped[str | None] = mapped_column(String, nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())