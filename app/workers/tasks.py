import asyncio

from celery import chain

from app.services.chunk_service import ChunkService
from app.services.embedding_service import GeminiEmbedding
from app.services.llm_service import GeminiLLM
from app.services.pdf_service import PDFService
from app.services.retrieval_service import RetrievalService
from app.services.telegram_api import send_message
from app.utils.celery_runner import run_async_with_db
from app.workers.celery import celery_app

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def chunker_orchestrator_task(self, pdf_id: int):
    pdf_service = PDFService()
    chunk_service = ChunkService()

    pdf = run_async_with_db(pdf_service.load_pdf,pdf_id)
    run_async_with_db(chunk_service.extract_and_chunk,pdf)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def embedding_orchestrator_task(self, pdf_id: int) -> None:
    chunk_service = ChunkService()
    embedding_service = GeminiEmbedding()

    # chunks = run_async_with_db(chunk_service.load_chunks, pdf_id)
    run_async_with_db(embedding_service.create_embeddings, pdf_id)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def output_orchestrator_task(self, chat_id: int, query: str):
    embedding_service = GeminiEmbedding()
    retrieval_service = RetrievalService()
    output_service = GeminiLLM()
    query_embedding = asyncio.run(embedding_service.create_query_embeddings(query))
    chunks = run_async_with_db(retrieval_service.retrieve, query_embedding)
    output = asyncio.run(output_service.generate_llm_output(query,chunks))
    asyncio.run(send_message(chat_id, output))

@celery_app.task
def chunk_embed_pipeline(pdf_id: int):
    chain(
        chunker_orchestrator_task.si(pdf_id),
        embedding_orchestrator_task.si(pdf_id),
    ).delay()