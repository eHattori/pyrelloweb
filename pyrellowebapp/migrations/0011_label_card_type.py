# Generated by Django 2.0.5 on 2018-05-25 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyrellowebapp', '0010_label_service_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='label',
            name='card_type',
            field=models.CharField(choices=[('bug', 'Bug'), ('value', 'Valor'), ('improvement', 'Melhorias'), ('ops', 'Ops'), ('others', 'Outros')], default='others', max_length=40),
        ),
    ]
