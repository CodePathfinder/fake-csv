from planekstz.celery import app

from .utils import generate_csv


@app.task
def fake_csv(schema_id, rows):
    generate_csv(schema_id, rows)

