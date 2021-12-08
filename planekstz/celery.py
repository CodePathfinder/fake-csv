# pip install celery
# pip install -U "celery[redis]"

# CMD - start worker - for development only - not in background
# celery -A planekstz worker -l INFO


import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planekstz.settings')

app = Celery('planekstz')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')