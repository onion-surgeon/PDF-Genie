# PDF-Genie

A Telegram-based document Q&A backend built with **FastAPI**, **Celery**, and **Retrieval-Augmented Generation (RAG)**. Upload a PDF, then ask natural-language questions about it and get answers grounded in the document's actual content.

## Overview

PDF-Genie lets a user upload a PDF through a Telegram bot. The document is chunked, embedded, and stored as vectors in PostgreSQL (via `pgvector`). When the user asks a question, the query is embedded and matched against the stored chunks using cosine similarity search, and the most relevant chunks are passed to an LLM to generate an answer.

## Try It

The bot is live on Telegram: [@genie_pdf_bot](https://web.telegram.org/k/#@genie_pdf_bot)

Upload a PDF and ask it questions to see the pipeline in action.

## Features

- PDF upload and storage via Telegram Bot API
- Asynchronous document processing pipeline using Celery
- Text chunking with token-aware splitting (`tiktoken` + `RecursiveCharacterTextSplitter`)
- Vector embeddings stored in PostgreSQL using `pgvector`
- Per-user semantic retrieval via cosine similarity search
- LLM-based answer generation grounded in retrieved chunks
- Centralized error handling with custom domain exceptions
- Dockerized multi-service deployment (API, worker, Redis)

## Architecture

```
1. User uploads PDF via Telegram
2. FastAPI webhook receives file, saves to disk + Postgres
3. Celery chain: chunk_text -> generate_embeddings -> notify_user
4. User sends a question
5. Query is embedded -> pgvector cosine similarity search -> top-5 chunks retrieved
6. Chunks + question sent to LLM -> answer returned to user via Telegram
```

## Tech Stack

- **Packet manager:** uv
- **Backend:** FastAPI
- **Task Queue:** Celery + Redis
- **Database:** PostgreSQL + pgvector
- **Migrations:** Alembic
- **Embeddings / LLM:** Gemini API
- **Interface:** Telegram Bot API
- **Infra:** Docker, Docker Compose, hosted on AIC Cloud (VPS)
- **CI/CD:** GitHub Actions

## Lessons learnt

- Discovered useful tools such as **Ngrok** to expose local APIs to public internet during development, , enabling testing of Telegram webhooks locally.
- Familiarised with structured logging for effective debugging 
- Got introduced to the concept of hashing the entire file contents to aid with uniqueness checking of files
- Exposure to the foundations of **RAG**- namely chunking, embedding, vector-storing and retrieving
- Experienced firsthand that Celery chains can't accommodate regular functions (not Celery tasks), since calling one executes it immediately instead of scheduling it as a step
- Understood that separate Docker containers don't share a filesystem by default, and how volume mounts are needed to bridge them


## Limitations

- File size limited to 20MB due to Telegram Bot API's download limit
- No OCR support — relies on an existing text layer in the PDF (works for text-based and pre-OCR'd scanned PDFs, not raw image-only scans)


