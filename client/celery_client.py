import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
