import os
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fakecsv.settings')

app = Celery('fakecsv')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

logger = get_task_logger(__name__)
