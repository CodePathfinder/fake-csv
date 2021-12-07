import json
import requests
from .models import Schema, DataSet
from django.conf import settings
import os
import time


def call_task(schema_id, rows=5):

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

    API_KEY = os.environ.get('API_KEY')

# ======================== REQUEST DATA ===========================    

    url = f'https://api.mockaroo.com/api/generate.csv?key={API_KEY}&count={rows}'
    
    try:
        # CSV response upon POST request
        response = requests.post(url, data=jfields)
        response.raise_for_status()
        print('Response: ', response)
        # print(response.encoding)

    except requests.RequestException as ex:
        message = f"Failed. RequestException: {ex}"
        return (response.status_code, None, None, message)

    # Parse response
    try:
        data = response.text  

    except (KeyError, TypeError, ValueError):
        message = "Parsing error"
        return (response.status_code, None, None, message)

# ========================== SAVE DATA =============================

    # date created
    date = time.strftime("%Y-%m-%d")

    # builf filename for cvs file
    filename = f'{rows}_{date}.csv'

    # Get the full path to upload response
    upload_path = upload_to(schema, filename)

    message = 'Processing'

    # Save data to csv file
    try:
        with open(upload_path, 'w') as file:
            file.write(data)
            message = 'Success'

    except Exception:
        message = 'Failed'
        return (response.status_code, date, None, message)
  
# ================= TODO UPDATE DB table DataSet here ====================

    DataSet.objects.create(
        user = schema.user,
        schema = schema,
        path = upload_path.split('schemas')[1].strip(),
        status = message,
    )

    return (response.status_code, date, filename, message)


def upload_to(schema, filename):     

    """Get the full path to upload response"""    
    # Build the path to ultimate media folder
    dir_path_to_file = f'{settings.MEDIA_ROOT}user_{schema.user.id}/schema_{schema.id}/'

    # create path folders in media (intermediate and ultimate), if not exist
    os.makedirs(dir_path_to_file, exist_ok=True)

    # return full path to csv file
    return (dir_path_to_file + filename)
        
