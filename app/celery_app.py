"""
Celery Application
"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "discovr_ai_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.services.script_ai", "app.services.video_ai", "app.services.campaign_ai", "app.services.brand_safety_ai", "app.services.creator_audit_ai"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 min max execution time for heavy video jobs
    worker_concurrency=2,  # Keep low to avoid massive memory spiking
    broker_connection_retry_on_startup=True,
)
