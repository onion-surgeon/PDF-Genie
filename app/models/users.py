from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Integer, String, DateTime, func
from datetime import datetime

from app.core.db.base import Base

class User(Base):
    __tablename__ = "users"

    userid: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger,unique=True,nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())