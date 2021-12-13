from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError

from .models import Schema, DataSet
from planekstz.celery import logger

import os
import time
import string
import random
import json
import requests


def generate_csv(schema_id, task_key, rows=30):

    # logger.info('START GENERATE CSV')

# ============== PREPARE BODY (schema) FOR API REQUEST ==============

    schema = Schema.objects.get(id = schema_id)

    colomns = schema.schematypes.all().order_by('order_num')

    fields = []

    for obj in colomns:

        d = {
            'name': obj.colomn_name,
            'type': obj.data_type.api_type
        }
        if obj.data_type.data_type in ['integer', 'text']:
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
    
    # logger.info('READY FOR API REQUEST TO %s', url)

    
    try:
        # CSV response upon POST request
        response = requests.post(url, data=jfields)
        response.raise_for_status()
        # logger.info('RESPONSE STATUS CODE: %s. TEXT FETCHED FROM REMOTE API', response.status_code)
        
    except requests.exceptions.RequestException as ex:
        # logger.info('FAILED. REQUEST EXCEPTION. STATUS_CODE: %s', response.status_code)
        return response.text


    # Parse response
    # logger.info('PARSING API RESPONSE')
    try:
        data = response.text  

    except (KeyError, TypeError, ValueError) as ex:
        # logger.info("FAILED. PARSING ERROR: %s", ex)
        return 

# ========================== SAVE DATA =============================

    # get timestamp
    date = time.strftime("%Y-%m-%d")

    # parse 
    mtk = task_key.split('.')[-1]

    # builf filename for cvs file
    filename = f'{rows}_{date}_{mtk}.csv'

    logger.info('START SAVING DATA TO CSV FILE %s', filename)

    # Get the full path to upload response
    upload_path = upload_to(schema, filename)

    # Save data to csv file
    try:
        with open(upload_path, 'w') as file:
            file.write(data)
            logger.info('DATA SAVED TO CSV FILE')

    except IOError as error:
        logger.info('FAILED. DATA NOT SAVED. EXCEPTION: %s', error)
        return
        
# ================= CREATE NEW OBJ WITH TASK DATA FOR DB TABLE DATASET ====================

    logger.info('START SAVING TASK DATA TO DATABASE')

    try:
        DataSet.objects.create(
        user = schema.user,
        schema = schema,
        rows = rows,
        path = upload_path.split('schemas')[1].strip(),
        monitor_task_key = mtk,
        )
        # logger.info('NEW OBJECT CREATED IN DATASET')

    except IntegrityError as error:
        # logger.info('NEW OBJECT IS NOT CREATED AND SAVED DUE TO INTEGRITY ERROR: %s', error)
        return

# ================= REMOVE TASK DATA FROM CACHE ====================

    if cache.has_key(task_key):
        cache.expire(task_key, timeout=0)
        # logger.info('CACHED TASK %s EXPIRED', task_key)

    logger.info('SUCCESS. TASK %s IS COMPLETED IN FULL', mtk)

    return


def upload_to(schema, filename):     

    """Get the full path to upload response"""    
    # Build the path to ultimate media folder
    dir_path_to_file = f'{settings.MEDIA_ROOT}user_{schema.user.id}/schema_{schema.id}/'

    # create path folders in media (intermediate and ultimate), if not exist
    os.makedirs(dir_path_to_file, exist_ok=True)

    # return full path to csv file
    return (dir_path_to_file + filename)
        

def monitor_task_key():
    """Generate random 6-sybmol string"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))  
