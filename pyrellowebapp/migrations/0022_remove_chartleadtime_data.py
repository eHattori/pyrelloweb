# Generated by Django 2.0.5 on 2018-06-15 17:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyrellowebapp', '0021_chartleadtime_leadtime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chartleadtime',
            name='data',
        ),
    ]