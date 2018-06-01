from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ('login', request.path))
    else:
        return render(request, 'home.html')

def import_cmd(request):
    from django.core.management import call_command
    call_command('import_trello_data')
    return HttpResponse("Command done")

def trigger(request):
    return HttpResponse("E5C6643AA2DDB88664EB1A0B103DA9E0")
