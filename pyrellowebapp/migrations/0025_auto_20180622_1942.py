# Generated by Django 2.0.5 on 2018-06-22 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyrellowebapp', '0024_transaction_end_date_cache'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='end_date_cache',
            field=models.DateField(blank=True, null=True),
        ),
    ]
