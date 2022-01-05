from django import forms

from .models import DataTypes, Schema, SchemaTypes


class SchemaForm(forms.ModelForm):

    class Meta:
        model = Schema
        fields = ['name', 'column_separator', 'string_character']
    
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control w-50 mb-3'}),
            'column_separator': forms.Select(attrs={'class': 'form-select w-50 mb-3'}),
            'string_character': forms.Select(attrs={'class': 'form-select w-50 mb-3'}),
        }


class SchemaTypesForm(forms.ModelForm):   

    cleaned_data = {}

    class Meta:
        model = SchemaTypes
        fields = ['column_name', 'data_type', 'range_from', 'range_to', 'order_num']
        labels = {
            'data_type': 'Type',
            'range_from': 'From',
            'range_to': 'To',
            'order_num': 'Order',
        }

        widgets = {
            'column_name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'data_type': forms.Select(attrs={'class': 'form-select mb-3'}),
            'range_from': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'range_to': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'order_num': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
        }
