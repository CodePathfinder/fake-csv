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

#=================================forms.Form (option 1)==========================================

# class SchemaForm(forms.Form):

#     COL_SEP_CHOICES = ( (',', 'Comma(,)'), ('\t', 'Tab'), ('|', "Pipe(|)"), (';', 'Semicolon(;)') )
#     STR_CHAR_CHOICES = ( ('"','Double-quote(")'), ("'","Single-quote(')"))

#     name = forms.CharField(max_length=100)
#     column_separator = forms.ChoiceField(choices = COL_SEP_CHOICES)
#     string_character = forms.ChoiceField(choices = STR_CHAR_CHOICES)
    
#     name.widget.attrs.update({'class': 'form-control w-50 mb-3'})
#     column_separator.widget.attrs.update({'class': 'form-select w-50 mb-3'})
#     string_character.widget.attrs.update({'class': 'form-select w-50 mb-3'})


#=================================forms.Form (option 2)==========================================

# class SchemaForm(forms.Form):

#     COL_SEP_CHOICES = ( (',', 'Comma(,)'), ('\t', 'Tab'), ('|', "Pipe(|)"), (';', 'Semicolon(;)') )
#     STR_CHAR_CHOICES = ( ('"','Double-quote(")'), ("'","Single-quote(')"))

#     name = forms.CharField(max_length=100)
#     column_separator = forms.CharField(
#         max_length=20,
#         widget = forms.Select(choices = COL_SEP_CHOICES),
#     )
#     string_character = forms.CharField(
#         max_length=20,
#         widget = forms.Select(choices = STR_CHAR_CHOICES),
#     )
    
#     name.widget.attrs.update({'class': 'form-control w-50 mb-3'})
#     column_separator.widget.attrs.update({'class': 'form-select w-50 mb-3'})
#     string_character.widget.attrs.update({'class': 'form-select w-50 mb-3'})


# def build_datatype_field():
#     kwargs = {}
#     kwargs["queryset"] = DataTypes.objects.all()
#     return forms.ModelsChoiceField(**kwargs)