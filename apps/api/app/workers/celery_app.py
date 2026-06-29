import os
try:
    from celery import Celery
except ImportError:
    # Minimal mock class for testing / execution in environments without celery installed
    class Celery:
        def __init__(self, *args, **kwargs):
            pass
        def task(self, *args, **kwargs):
            return lambda fn: fn

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery(
    "nomen_workers",
    broker=redis_url,
    backend=redis_url
)

# Configuration overrides
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True
)
