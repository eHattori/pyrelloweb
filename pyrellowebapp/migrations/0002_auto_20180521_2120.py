# Generated by Django 2.1a1 on 2018-05-21 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyrellowebapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='transactions',
        ),
        migrations.AddField(
            model_name='transaction',
            name='card',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='pyrellowebapp.Card'),
            preserve_default=False,
        ),
    ]
