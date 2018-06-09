from __future__ import absolute_import
from celery import shared_task

@shared_task
def import_trello_data():
    from django.core.management import call_command
    call_command('import_trello_data')

@shared_task
def import_jira_data():
    from django.core.management import call_command
    call_command('import_jira_data')

@shared_task
def graphs_cache():
    from django.core.management import call_command
    call_command('graphs_cache')


