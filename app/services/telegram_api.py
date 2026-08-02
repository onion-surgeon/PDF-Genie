import httpx

from app.core.config import settings 

async def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "MarkdownV2"
            },
        )

        response.raise_for_status()

async def download_file_telegram(file_id: str) -> bytes:
    base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{base_url}/getFile",
            params={"file_id": file_id},
        )
        response.raise_for_status()

        data = response.json()
        file_path = data["result"]["file_path"]

        file_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"

        file_response = await client.get(file_url)
        file_response.raise_for_status()

        return file_response.content   