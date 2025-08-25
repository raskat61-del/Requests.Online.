from celery import Celery
import os
from app.core.config import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "analytics_bot",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    include=[
        "app.tasks.search_tasks",
        "app.tasks.analysis_tasks", 
        "app.tasks.report_tasks",
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_serializer_retries=3,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks()