web: gunicorn fakecsv.wsgi --log-file -
worker: celery -A fakecsv worker -l INFO
