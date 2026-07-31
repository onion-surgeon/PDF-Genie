
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunks import Chunk

class RetrievalService():
    
    async def retrieve(self,db: AsyncSession,pdf_id: int,query_embedding: list[float],
        top_k: int = 5,) -> list[Chunk]:

        stmt = (select(Chunk).where(Chunk.pdfid == pdf_id).order_by(
                Chunk.embedding.cosine_distance(query_embedding)
            ).limit(top_k)
        )

        result = await db.execute(stmt)

        return result.scalars().all()
    
