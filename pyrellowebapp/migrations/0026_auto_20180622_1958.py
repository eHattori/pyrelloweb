# Generated by Django 2.0.5 on 2018-06-22 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyrellowebapp', '0025_auto_20180622_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='end_date_cache',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
