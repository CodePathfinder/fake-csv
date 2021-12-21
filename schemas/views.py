from django.http.response import JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import IntegrityError
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .models import User, Schema, SchemaTypes, DataTypes, DataSet
from .forms import SchemaForm, SchemaTypesForm
from .tasks import fake_csv, del_csv
from .utils import monitor_task_key

import time
import json


def index(request):
    
    schemas = Schema.objects.filter(user=request.user.id)

    context = {
        'schemas': schemas
    }
    return render(request, "schemas/index.html", context=context)


class SchemaCreate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        
        """render empty forms """

        schema_form = SchemaForm()
        type_form = SchemaTypesForm()
        
        context = {
            'schema_form': schema_form, 
            'type_form': type_form 
        }
        return render(request, "schemas/schema.html", context=context)
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request):

        """create new Schema object"""

        bound_schema_form = SchemaForm(request.POST)

        if bound_schema_form.is_valid():          
          
            new_schema = Schema(
                user = request.user,
                name = bound_schema_form.cleaned_data['name'],
                colomn_separator = bound_schema_form.cleaned_data['colomn_separator'],
                string_character = bound_schema_form.cleaned_data['string_character']
            )    

            try:
                new_schema.save()

            except IntegrityError:
                messages.error(request, f'Failure to create new schema object')
                # return to form page (schema.html)                              
                context = {
                    'schema_form': bound_schema_form, 
                    'type_form': SchemaTypesForm() 
                }
                return render(request, "schemas/schema.html", context=context)

        """create colomn(s) (SchemaTypes objects) for new schema object"""
   
        # get list of "POST" dictionary keys starting with 'colomn_name'
        cols = [item for item in request.POST if item.startswith('colomn_name')]
        
        # get list of 'indexes' that are generated by JS addcolomn function for each colomn instance 
        index_list = [int(col.split('_')[-1].strip()) for col in cols]
        
        # iterate over index list creating SchemaTypes
        for i in index_list:
            
            # get DataType object by ID
            dtype_id = request.POST.get(f'data_type_{i}')
            dtype_obj = DataTypes.objects.get(id = int(dtype_id))

            # cast range values
            rng_from = request.POST.get(f'range_from_{i}')
            range_from = int(rng_from) if rng_from else None
            rng_to = request.POST.get(f'range_to_{i}')
            range_to = int(rng_to) if rng_to else None

            # create colomn object           
            try:
                col_name = request.POST.get(f'colomn_name_{i}')
                SchemaTypes.objects.create(
                    schema = new_schema,
                    colomn_name = col_name,
                    data_type = dtype_obj,
                    range_from = range_from,
                    range_to = range_to,
                    order_num = request.POST.get(f'order_num_{i}'),                
                )
            except IntegrityError:
                messages.error(request, f'Failure to create column {col_name}')
                # return to form page (schema.html)                              
                context = {
                    'schema_form': bound_schema_form, 
                    'type_form': SchemaTypesForm() 
                }
                return render(request, "schemas/schema.html", context=context)
        messages.success(request, f"New schema {new_schema.name} is created.")
        return redirect('index')


@csrf_exempt
@login_required
def delete_schema(request, schema_id):
    
    """ delete schema with all related schematypes, 
        delete related dataset objects and uploaded datasets """
    
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required"}, safe=False, status=400)
    
    else:
        (request.method)
        try:
            schema = Schema.objects.get(id=schema_id)
        except Schema.DoesNotExist:
            return JsonResponse({"error": "Selected schema is not found"}, safe=False, status=404)
        
        schema_name = schema.name

        schema_datasets = DataSet.objects.filter(schema=schema_id)
        path_list = [str(ds.path) for ds in schema_datasets] if schema_datasets else []

        # delete schema with all related SchemaTypes and DataSet objects (on_delete=models.CASCADE) 
        schema.delete()

        # start deletion of the uploaded datasets in the background
        task_id = del_csv.delay(path_list)   
        return JsonResponse({"success": f"schema {schema_name} deleted", "task_id": f"{task_id}"}) 


class SchemaUpdate(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, schema_id):
        
        """render pre-populated form"""
        
        schema = Schema.objects.get(id=schema_id)

        schema_form = SchemaForm(instance=schema)
        
        type_forms_data = [(SchemaTypesForm(instance=type), type.id) for type in schema.schematypes.all()]
        
        context = {
            'schema': schema,
            'schema_form': schema_form,
            'type_forms_data': type_forms_data
        }
        return render(request, "schemas/schema_update.html", context=context)
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request, schema_id):

        """update existing Schema object"""

        updated_schema_form = SchemaForm(request.POST)

        if updated_schema_form.is_valid():          
          
            schema = Schema.objects.get(id=schema_id)
            
            updated_schema = SchemaForm(request.POST, instance=schema)
            
            try:
                updated_schema.save()
                
            except IntegrityError:
                messages.error(request, f'Failure to update schema {schema.name}')
                # return to schema_update page (pre-populated form)                              
                return redirect('schema_update', schema_id)
        
        # update existing SchemaTypes objects
        
        existing_cols = SchemaTypes.objects.filter(schema__id=schema_id)

        existing_cols_id_list = [item.id for item in existing_cols]

        # get list of "POST" dictionary keys starting with 'colomn_name'
        updated_cols = [item for item in request.POST if item.startswith('colomn_name')]
        
        # get list of 'indexes' that are generated by JS addcolomn function for each colomn instance 
        updated_cols_id_list = [int(col.split('_')[-1].strip()) for col in updated_cols]
        
        # iterate over existing SchemaTypes objects related to updated schema
        for col_id in existing_cols_id_list:
            # if col_id is not mentioned in request.POST, it implies that user deleted that column
            if col_id not in updated_cols_id_list:
                SchemaTypes.objects.get(id=col_id).delete()
            else:
                # get DataType object by ID from request.POST dictionary and DB
                dtype_id = request.POST.get(f'data_type_{col_id}')
                dtype_obj = DataTypes.objects.get(id = int(dtype_id))

                # cast range values
                rng_from = request.POST.get(f'range_from_{col_id}')
                range_from = int(rng_from) if rng_from else None
                rng_to = request.POST.get(f'range_to_{col_id}')
                range_to = int(rng_to) if rng_to else None

                # collect updated column data from request.POST dictionary
                col_form_dict = {
                    'schema': schema,
                    'colomn_name': request.POST.get(f'colomn_name_{col_id}'),
                    'data_type': dtype_obj,
                    'range_from': range_from,
                    'range_to': range_to,
                    'order_num': request.POST.get(f'order_num_{col_id}'),     
                }

                # get existing SchemaTypes object by col_id (ID)
                st_object = SchemaTypes.objects.get(id=col_id)
                
                # update SchemaTypes object           
                try:
                    updated_column = SchemaTypesForm(col_form_dict, instance=st_object)
                    updated_column.save()
                except IntegrityError:
                    messages.error(request, f'Failure to update object with column name {st_object.colomn_name}')
                    # return to schema_update page (pre-populated form)                              
                    return redirect('schema_update', schema_id)
        # messages.success(request, f"Schema {updated_schema.name} is updated.")
        messages.success(request, f'Schema "{schema.name}" is updated.')
        return redirect('index')


class Datasets(View):
    
    @method_decorator(login_required(login_url='login'))
    def get(self, request, schema_id):
        
        try:
            s = Schema.objects.get(id = schema_id)
        except Schema.DoesNotExist:
            return JsonResponse({"error": "Schema not found"}, safe=False, status=404)
        
        # get dataset collection from DB
        schema_data = s.data.all()
        # get from cache pending tasks 
        pending_data = []
        for key in cache.keys(f'*schema-{schema_id}*'):
            task_data = {}
            task_data.update(
                task_key = key.split('.')[-1],
                task_id = cache.get(key)['task_id'],
                task_created = cache.get(key)['date']
            )
            pending_data.append(task_data)
 
        context = {
            'schema': s,
            'schema_data': schema_data,
            'pending_data': pending_data
        }

        return render(request, "schemas/datasets.html", context=context)
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request, schema_id):
        
        rows = request.POST['rows']
        
        # validate rows input:
        if not rows:
            return JsonResponse({'ValidationError': 'rows field is required'}, status=400) 
        try: 
            rows = int(rows)
        except ValueError:
            return JsonResponse({'ValidationError': 'rows should be an integer'}, status=400) 
        if rows < 1 or rows > 1000:
            return JsonResponse({'ValidationError': 'please enter positive integer in range for 1 to 1000'}, status=400) 

        # generate key for monitoring tasks in cache
        mtk = monitor_task_key()
        task_key = f'schema-{schema_id}.{mtk}'

        # task is launched  
        task_id = fake_csv.delay(schema_id, task_key, rows)
        
        task_data = {
            'task_id': task_id,
            'date': time.strftime("%Y-%m-%d")
        }

        # place task key/task data in cache
        cache.set(task_key, task_data, timeout=60*30)
 
        return redirect('datasets', schema_id)


@login_required
def status_check(request, mtk):

    if DataSet.objects.filter(monitor_task_key__iexact=mtk).exists():
        obj = DataSet.objects.get(monitor_task_key__iexact=mtk)
        return JsonResponse(obj.serialize())
    else:
        return JsonResponse({"url": None})
    

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        
        # Ensure password matches confirmation
        password = request.POST["password"]
        
        if not username or not password:
            messages.error(request, "Invalid request. Please enter username and password.")
            return render(request, "schemas/register.html")
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords does not match.")
            return render(request, "schemas/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(request, "schemas/register.html")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "schemas/register.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(request, "schemas/login.html")
    else:
        return render(request, "schemas/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

