# Generated by Django 2.1a1 on 2018-05-21 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyrellowebapp', '0004_auto_20180521_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateTimeField(),
        ),
    ]