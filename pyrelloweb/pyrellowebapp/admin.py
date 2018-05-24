from django.contrib import admin
from pyrellowebapp import models

class ColumnInLine(admin.StackedInline):
    model = models.Column


class BoardAdmin(admin.ModelAdmin):
    inlines = [ColumnInLine,] 

admin.site.register(models.Board, BoardAdmin)
