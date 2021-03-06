from django.contrib import admin
from pyrellowebapp import models

class ColumnInLine(admin.StackedInline):
    model = models.Column
    extra = 0
    fields = ('importance_order', 'leadtime_period','board_position', 'active',) 
    ordering = ('board_position',)

class LabelInLine(admin.StackedInline):
    model = models.Label
    extra = 0
    fields = ('service_class', 'card_type')
    ordering = ('name',)

class BoardAdmin(admin.ModelAdmin):
    inlines = [ColumnInLine, LabelInLine] 

admin.site.register(models.Board, BoardAdmin)
