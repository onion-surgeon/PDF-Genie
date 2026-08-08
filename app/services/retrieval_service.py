
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunks import Chunk
from app.models.pdf import PDF

class RetrievalService():
    
    async def retrieve(self,db: AsyncSession,user_id: int, query_embedding: list[float],
        top_k: int = 5,) -> list[Chunk]:

        query = (
            select(Chunk)
            .join(PDF, Chunk.pdfid == PDF.pdfid)
            .where(PDF.userid == user_id)
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        result = await db.execute(query)
        chunks = result.scalars().all()

        return chunks
    
