# Generated by Django 2.1a1 on 2018-05-21 21:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyrellowebapp', '0003_auto_20180521_2138'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='transaction',
            unique_together={('column', 'date')},
        ),
    ]