# Generated by Django 3.2.9 on 2021-12-13 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schemas', '0007_auto_20211208_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='path',
            field=models.FileField(blank=True, upload_to='media/'),
        ),
    ]
