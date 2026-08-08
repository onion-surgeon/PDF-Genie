from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.logging_config import setup_logging


setup_logging()

celery_app = Celery(
    "PDF-Genie",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)
