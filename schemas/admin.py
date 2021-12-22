from django.contrib import admin
from .models import User, DataTypes, Schema, SchemaTypes, DataSet


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')
    list_display_links = ('id', 'username')
    search_fields = ('username',)


class DataTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_type', 'api_type')
    list_display_links = ('id', 'data_type', 'api_type')
    order_by = 'data_type'


class SchemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'created_at')
    list_display_links = ('id', 'user', 'name')
    order_by = 'user'
    search_fields = ('user', 'name')


class SchemaTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema', 'column_name', 'data_type', 'range_from', 'range_to')
    list_display_links = ('schema', 'column_name', 'data_type')
    order_by = 'data_type'
    search_fields = ('schema', 'column_name', 'range_from')


class DataSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema', 'rows', 'path', 'monitor_task_key', 'created_at')
    list_display_links = ('rows', 'path', 'monitor_task_key')
    order_by = '-created_at'


admin.site.register(User, UserAdmin)
admin.site.register(DataTypes, DataTypesAdmin)
admin.site.register(Schema, SchemaAdmin)
admin.site.register(SchemaTypes, SchemaTypesAdmin)
admin.site.register(DataSet, DataSetAdmin)
