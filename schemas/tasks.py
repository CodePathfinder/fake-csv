from planekstz.celery import app

from .utils import generate_csv, delete_datasets


@app.task
def fake_csv(schema_id, task_key, rows):
    result = generate_csv(schema_id, task_key, rows)
    return result


@app.task
def del_csv(path_list):
    result = delete_datasets(path_list)
    return result

