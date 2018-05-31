from django.shortcuts import redirect
from django.shortcuts import render

def home(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ('login', request.path))
    else:
        return render(request, 'home.html')
