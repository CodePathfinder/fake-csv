from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):

    def __str__(self):
        return self.username


class DataTypes(models.Model):

    data_type = models.CharField(max_length=100)
    api_type = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.data_type

    class Meta:
        verbose_name_plural  = 'DataTypes'
        ordering = ['data_type']


class Schema(models.Model):

    COL_SEP_CHOICES = ( (',', 'Comma(,)'), ('|', "Pipe(|)"), (';', 'Semicolon(;)') )
    STR_CHAR_CHOICES = ( ('"','Double-quote(")'), ("'","Single-quote(')"))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schemas")
    name = models.CharField(max_length=100)
    column_separator = models.CharField(max_length=20, choices = COL_SEP_CHOICES, default='Comma(,)')
    string_character = models.CharField(max_length=20, choices = STR_CHAR_CHOICES, default='Double-quote(")')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'name'),)
    
    def __str__(self):
        return self.name
    

class SchemaTypes(models.Model):

    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, related_name="schematypes")
    column_name = models.CharField(max_length=100)
    data_type = models.ForeignKey(DataTypes, on_delete=models.CASCADE, related_name="datatypes")
    range_from = models.IntegerField(blank=True, null=True, default=None)
    range_to = models.IntegerField(blank=True, null=True, default=None)
    order_num = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.column_name

    class Meta:
        verbose_name_plural  = 'SchemaTypes'


class DataSet(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dataset")
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, related_name="data")
    rows = models.IntegerField(blank=True, null=True)
    path = models.FileField(upload_to='media/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    monitor_task_key = models.CharField(max_length=10, blank=True, null=True)
    
    def serialize(self):
        return { "url": self.path.url }

    def __str__(self):
        return self.monitor_task_key