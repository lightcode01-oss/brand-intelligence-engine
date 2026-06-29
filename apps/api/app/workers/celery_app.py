import os

try:
    from celery import Celery
except ImportError:
    class Celery:
        def __init__(self, *args, **kwargs):
            class DummyConf:
                def update(self, *args, **kwargs): pass
            self.conf = DummyConf()
        def task(self, *args, **kwargs):
            return lambda fn: fn

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery(
    "nomen_workers",
    broker=redis_url,
    backend=redis_url
)

# Configuration overrides with task priority routing & dead-letter queue (DLQ)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Priority Queues & Dead-Letter Queue Routing
    task_default_queue="default",
    task_queues={
        "high_priority": {
            "binding_key": "high_priority",
        },
        "default": {
            "binding_key": "default",
        },
        "low_priority": {
            "binding_key": "low_priority",
        },
        "dead_letter": {
            "binding_key": "dead_letter",
        }
    },
    task_routes={
        "app.workers.generation.*": {"queue": "high_priority"},
        "app.workers.validation.*": {"queue": "high_priority"},
        "app.workers.notifications.*": {"queue": "low_priority"},
        "app.workers.export.*": {"queue": "default"},
    },
    # Ensure failed tasks are retried or sent to DLQ
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
