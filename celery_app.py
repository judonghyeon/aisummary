from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    "app",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["tasks"]  # 🔥 중요
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",

    # 🔥 큐 분리
    task_routes={
        "tasks.download": {"queue": "download"},
        "tasks.transcribe": {"queue": "stt"},
        "tasks.summarize": {"queue": "summary"},
    },

    # 🔥 안정성
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)