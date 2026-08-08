import logging

from abc import ABC, abstractmethod

from app.core.config import settings
from google import genai
from google.genai import types
from app.models.chunks import Chunk

logger = logging.getLogger(__name__)
class LLMService(ABC):

    system_instruction = '''You are answering questions about a PDF.

    Use ONLY the information contained in the provided context.

    Context:
    [chunk 1]
    [chunk 2]
    [chunk 3]

    Question:
    [user's question]

    Instructions:
    - Answer the question using only the context.
    - Do not use outside knowledge.
    - If the context does not contain enough information to answer confidently, say that the answer was not found in the document.'''

    @abstractmethod
    async def generate_llm_output(self, query: str, chunks: list[Chunk]) -> str:
        pass

class GeminiLLM(LLMService):
    def __init__ (self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate_llm_output(self, query: str, chunks: list[Chunk]) -> str:
        
        context = "\n\n".join(
            chunk.content for chunk in chunks
        )

        prompt = f"""
            {self.system_instruction}

            Context:
            {context}

            Question:
            {query}
            """

        try:
            response = await self.client.aio.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents= prompt,
            )

            result = response.text

            return result

        except Exception as e:
            logger.warning(f"Gemini chunks organiser has failed : {str(e)}")
            raise