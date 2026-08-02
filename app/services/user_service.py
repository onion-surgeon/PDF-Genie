from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pdf import PDF
from app.models.users import User


class UserService:

    async def get_user_id_from_telegram_id(self, db: AsyncSession, t_id: int) -> int | None:
        query = select(User).where(User.telegram_id == t_id)
        result = await db.execute(query)
        user = result.scalars().first()
        return user.userid
    
    async def check_user_pdf_exists(self, db: AssertionError,user_id:int):
        query = select(PDF).where(PDF.userid == user_id)
        id = await db.execute(query)
        return id.scalars().first()