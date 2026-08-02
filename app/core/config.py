from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    TELEGRAM_BOT_TOKEN: str
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str
    UPLOAD_DIR: Path
    REDIS_URL: str
settings = Settings()