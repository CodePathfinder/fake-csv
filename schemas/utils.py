from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError

from .models import Schema, DataSet
from fakecsv.celery import logger
from fakecsv import settings
from django.core.files.storage import default_storage

import string
import random
import json
import requests


def generate_csv(schema_id, task_key, rows=30):

    logger.info('START GENERATE CSV')

# ============== PREPARE BODY (schema) FOR API REQUEST ==============

    schema = Schema.objects.get(id = schema_id)

    columns = schema.schematypes.all().order_by('order_num')

    fields = []

    for obj in columns:

        d = {
            'name': obj.column_name,
            'type': obj.data_type.api_type
        }
        if obj.data_type.data_type in ['Integer', 'Text']:
            if obj.range_from:
                d['min'] = obj.range_from
            if obj.range_to:
                d['max'] = obj.range_to
            d['decimals'] = 0

        fields.append(d)

    jfields = json.dumps(fields)

    # logger.info('REQUEST BODY/SCHEMA IS BUILT')

# ======================== REQUEST DATA ===========================    
    
    url = f'https://api.mockaroo.com/api/generate.csv?key={settings.MOCKAROO_API_KEY}&count={rows}'
    
    logger.info(f'READY FOR API REQUEST TO {url}')
    
    try:
        # CSV response upon POST request
        response = requests.post(url, data=jfields)
        response.raise_for_status()
        logger.info('RESPONSE STATUS CODE: %s. TEXT FETCHED FROM REMOTE API', response.status_code)
        
    except requests.exceptions.RequestException as ex:
        logger.info('FAILED. REQUEST EXCEPTION. STATUS_CODE: %s', response.status_code)
        return response.text


    # Parse response
    # logger.info('PARSING API RESPONSE')
    try:
        data = response.text  

    except (KeyError, TypeError, ValueError) as ex:
        # logger.info("FAILED. PARSING ERROR: %s", ex)
        return 

# ========================== SAVE DATA TO S3 BUCKET =============================

    # parse 
    mtk = task_key.split('.')[-1]

    # builf filename for cvs file
    filename = f'{mtk}.csv'

    logger.info('START SAVING DATA TO CSV FILE %s', filename)

    # Get the full path to upload response
    upload_path = f'media/{filename}'

    # Save data to csv file
    try:
        with default_storage.open(upload_path, 'w') as file:
            file.write(data)
            logger.info(f'DATA SAVED REMOTELY TO S3 WITH FILENAME {upload_path}')

    except IOError as error:
        logger.info(f'FAILED. DATA NOT SAVED. EXCEPTION: {error}')
        return

    logger.info(f'DEFAULT STORAGE URL: {default_storage.url(upload_path)}')
  
# ================= CREATE NEW OBJ WITH TASK DATA FOR DB TABLE DATASET ====================
 
    try:
        obj = DataSet.objects.create(
            user = schema.user,
            schema = schema,
            rows = rows,
            path = upload_path,
            monitor_task_key = mtk,
        )
        logger.info(f'NEW OBJECT CREATED IN DATASET, PATH {obj.path}')

    except IntegrityError as error:
        logger.info(f'NEW OBJECT IS NOT CREATED AND SAVED DUE TO INTEGRITY ERROR: {error}')
        return

# ================= REMOVE TASK DATA FROM CACHE ====================

    if cache.has_key(task_key):
        cache.expire(task_key, timeout=0)
        logger.info(f'CACHED TASK {task_key} EXPIRED')

    logger.info(f'SUCCESS. TASK {mtk} IS COMPLETED IN FULL')

    return


def monitor_task_key():
    """Generate random 6-sybmol string"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))  


def delete_datasets(path_list):
    """Delete csv file from media folder in S3 bucket"""
    if path_list:
        for path in path_list:
            filename = path.split("/")[1].split(".")[0]
            if default_storage.exists(path):                
                default_storage.delete(path)
                logger.info(f'FILE {filename} DELETED')
            else:
                logger.info(f'FILE {filename}.csv DOES NOT EXIST')
    else:
        logger.info(f'NO RELATED CSV FILE IN S3 BUCKET TO BE DELETED')
    return
