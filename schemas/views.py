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

from .models import Schema, SchemaTypes, DataTypes, DataSet
from .forms import SchemaForm, SchemaTypesForm
from .tasks import fake_csv
from .utils import monitor_task_key

import time


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

            except IntegrityError as ex:
                # exception message
                error_message = ex
                # return to form page (schema.html)                              
                context = {
                    'message': error_message,
                    'schema_form': bound_schema_form, 
                    'type_form': SchemaTypesForm() 
                }
                return render(request, "schemas/schema.html", context=context)

        """create colomn(s) (SchemaTypes objects) for new schema object"""
   
        # get list of "POST" dictionary keys starting with 'colomn_name'
        cols = [item for item in request.POST if item.startswith('colomn_name')]
        
        # get list of 'indexes' that are generated by JS addColomn function for each colomn instance 
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
                SchemaTypes.objects.create(
                    schema = new_schema,
                    colomn_name = request.POST.get(f'colomn_name_{i}'),
                    data_type = dtype_obj,
                    range_from = range_from,
                    range_to = range_to,
                    order_num = request.POST.get(f'order_num_{i}'),                
                )

            except IntegrityError as ex:
                # exception message
                error_message = ex
                # return to form page (schema.html)                              
                context = {
                    'message': error_message,
                    'schema_form': bound_schema_form, 
                    'type_form': SchemaTypesForm() 
                }
                return render(request, "schemas/schema.html", context=context)

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
def status_check(requst, mtk):

    if DataSet.objects.filter(monitor_task_key__iexact=mtk).exists():
        obj = DataSet.objects.get(monitor_task_key__iexact=mtk)
        return JsonResponse(obj.serialize())
    else:
        return JsonResponse({"url": None})
    

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
            return render(request, "schemas/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "schemas/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

