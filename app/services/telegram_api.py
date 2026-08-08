import httpx, logging
from httpx import Response
from tenacity import retry, retry_if_exception_type, stop_after_attempt
from app.core.config import settings
from app.exceptions.types import TelegramAPIError 

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(TelegramAPIError)
)
async def request_url(client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Response:
    response = await client.request(method, url, **kwargs)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        data = e.response.json()
        raise TelegramAPIError(data.get("error_code"), data.get("description"))
    return response

async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        response = await request_url(client, "POST", url, json={"chat_id": chat_id, "text": text})

async def download_file_telegram(file_id: str) -> bytes:
    base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


    async with httpx.AsyncClient() as client:

        response = await request_url(client, "GET",  f"{base_url}/getFile", params={"file_id": file_id} )

        data = response.json()
        file_path = data["result"]["file_path"]

        file_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"

        file_response = await request_url(client, "GET", file_url)

        return file_response.content 

async def notify_user_safe(chat_id: int, text: str):
    try:
        await send_message(chat_id, text)
    except Exception as e:
        logger.error(f"Failed to notify chat {chat_id}: {e}", exc_info=True)
