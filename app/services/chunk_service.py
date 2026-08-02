from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select

from app.models.chunks import Chunk
from app.models.pdf import PDF, Status
from app.models.chunks import ChunkStatus
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.document_loaders import PyMuPDFLoader

import tiktoken

class ChunkService:

    def __init__(self):
        pass

    async def extract_and_chunk(self, db:AsyncSession, pdf:PDF) -> None:
        chunks = await self.extract_text_and_chunk(db, pdf)
        await self.store_chunks(db, pdf, chunks)

    async def load_chunks(self, db:AsyncSession, pdf_id:int) -> list[Chunk]:
        query = select(Chunk).where(Chunk.pdfid == pdf_id)
        pdf = await db.execute(query)
        return pdf.scalars().all()
    
    async def extract_text_and_chunk(self, db:AsyncSession, pdf:PDF) -> list[Chunk]:
        pdf.status = Status.PROCESSING
        await db.commit() #already fetched pdf
        storage_path = pdf.storage_path
        document = PyMuPDFLoader(storage_path).load()
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500,
        chunk_overlap=100,
    ) 
        chunks = splitter.split_documents(document)
        encoding = tiktoken.get_encoding("cl100k_base")
        result = []
        for i, doc in enumerate(chunks):
            chunk_record = Chunk(
                pdfid = pdf.pdfid, 
                content = doc.page_content,
                status = ChunkStatus.PENDING,
                token_count = len(encoding.encode(doc.page_content)),
                page_number = doc.metadata.get("page")                
            )
            result.append(chunk_record)
        return result        

    async def store_chunks(self, db:AsyncSession, pdf:PDF, chunks:Chunk):
        if chunks:
            try:
                db.add_all(chunks)
                pdf.status = Status.CHUNKED
                await db.commit()
            except Exception as e:
                await db.rollback()
                pdf.status = Status.FAILED
                pdf.failure_reason = str(e)
                raise e            
        return