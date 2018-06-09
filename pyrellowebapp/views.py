from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse
from pyrellowebapp import tasks

def home(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ('login', request.path))
    else:
        return render(request, 'home.html')

def import_trello_cmd(request):
    tasks.import_trello_data.delay()
    return HttpResponse("Command done")

def import_jira_cmd(request):
    tasks.import_jira_data.delay()
    return HttpResponse("Command done")

def graph_cmd(request):
    tasks.graphs_cache.delay()
    return HttpResponse("Command done")

def trigger(request):
    return HttpResponse("E5C6643AA2DDB88664EB1A0B103DA9E0")
