# Generated by Django 2.0.5 on 2018-06-22 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyrellowebapp', '0022_remove_chartleadtime_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='end_date_cache',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
