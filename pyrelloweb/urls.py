"""pyrelloweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from pyrellowebapp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('import_trello/', views.import_trello_cmd, name="import_trello_cmd"),
    path('import_jira/', views.import_jira_cmd, name="import_jira_cmd"),
    path('import/', views.import_trello_cmd, name="import_trello_cmd"),
    path('graph/', views.graph_cmd, name="graph_cmd"),
    path('login/', auth_views.login, name='login'),
    path('ATriggerVerify.txt', views.trigger, name="trigger"),
]
