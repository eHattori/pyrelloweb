from django.contrib import admin
from pyrellowebapp import models

class ColumnInLine(admin.StackedInline):
    model = models.Column
    fields = ('importance_order', 'leadtime_period','board_position', 'active',) 

class LabelInLine(admin.StackedInline):
    model = models.Label
    fields = ('service_class', 'card_type')

class BoardAdmin(admin.ModelAdmin):
    inlines = [ColumnInLine, LabelInLine] 

admin.site.register(models.Board, BoardAdmin)
