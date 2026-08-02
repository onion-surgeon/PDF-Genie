from abc import ABC, abstractmethod
import asyncio

from openai import AsyncOpenAI
from google import genai
from google.genai import types
from sqlalchemy import select, update
from app.core.config import settings
from app.models.chunks import Chunk, ChunkStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

BATCH_SIZE = 10

class EmbeddingService(ABC):
    
    @abstractmethod
    async def create_embeddings(self, db: AsyncSession, chunks: list[Chunk]) -> None:
        pass

    @abstractmethod
    async def create_query_embeddings(self, db: AsyncSession, text: str) -> list[float]:
        pass

class GPTEmbedding(EmbeddingService):
    def __init__ (self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class GeminiEmbedding(EmbeddingService):
    def __init__ (self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    
    async def create_embeddings(self, db: AsyncSession, pdf_id: int):
        result = await db.execute(
            select(Chunk).where(
                Chunk.pdfid == pdf_id,
                Chunk.status == ChunkStatus.PENDING,
            )
        )
        chunks = result.scalars().all()

        if not chunks:
            return

        batch = []
        try:
            for i in range(0, len(chunks), BATCH_SIZE):
                batch = chunks[i:i + BATCH_SIZE]
                text = [chunk.content for chunk in batch]

                response = await self.client.aio.models.embed_content(
                    model="gemini-embedding-2",
                    contents=[
                        types.Content(parts=[types.Part.from_text(text=t)])
                        for t in text
                    ],
                    config=types.EmbedContentConfig(output_dimensionality=768),
                )

                assert len(batch) == len(response.embeddings)

                for chunk, result_item in zip(batch, response.embeddings):
                    if result_item:
                        chunk.embedding = result_item.values
                        chunk.status = ChunkStatus.EMBEDDED
                        chunk.failure_reason = ''

                await db.commit()
                await asyncio.sleep(10)

        except Exception as e:
            await db.rollback()
            for chunk in batch:
                chunk.status = ChunkStatus.FAILED
                chunk.failure_reason = str(e)
            await db.commit()
            raise
        
    async def create_query_embeddings(self, text: str) -> list[float]:

        response = await self.client.aio.models.embed_content(
                model="gemini-embedding-2",
                contents= text,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
    
        return response.embeddings[0].values
