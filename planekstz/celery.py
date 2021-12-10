# pip install celery
# pip install -U "celery[redis]"

# CMD - start worker - for development only - not in background
# celery -A planekstz worker -l INFO


import os
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planekstz.settings')

app = Celery('planekstz')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

logger = get_task_logger(__name__)
