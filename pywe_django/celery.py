from __future__ import absolute_import, unicode_literals
import os
import sys
from celery import Celery


from kombu import Exchange, Queue
from celery.schedules import crontab

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pywe_django.settings')

DJANGO_IN_DOCKER_DEBUG = os.environ.get("DJANGO_DEBUG", None)

redis_broker_location = "127.0.0.1" if DJANGO_IN_DOCKER_DEBUG is None else "redis://redis:6379/2"
redis_backend_location = "127.0.0.1" if DJANGO_IN_DOCKER_DEBUG is None else "redis://redis:6379/3"

app = Celery('pywe_django', broker=redis_broker_location, backend=redis_backend_location)

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.CELERY_TIMEZONE = 'Asia/Chongqing'

app.conf.update(
    CELERYBEAT_SCHEDULE={
        # "demo_minutes_task": {
        #     'task': "pywe_django.tasks.demo_minutes_task",
        #     'schedule': crontab(minute='*')
        # },
    }
)

CELERY_DEFAULT_QUEUE = "default"

CELERY_QUEUES = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("demo", Exchange("demo"), routing_key="demo")
)

CELERY_ROUTES = {
    'tasks.demo_task': {'queue': 'demo', 'routing_key': 'demo'},
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
