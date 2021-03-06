# Generated by Django 3.2.9 on 2021-12-08 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schemas', '0006_auto_20211207_1537'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='status',
        ),
        migrations.RemoveField(
            model_name='schema',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='schema',
            name='is_deleted',
        ),
        migrations.RemoveField(
            model_name='schematypes',
            name='is_deleted',
        ),
        migrations.AddField(
            model_name='dataset',
            name='monitor_task_key',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='dataset',
            name='rows',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='path',
            field=models.CharField(max_length=128),
        ),
    ]
