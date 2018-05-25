from django.db import models
from datetime import datetime

import numpy

class Board(models.Model):
    name = models.CharField(max_length=250)
    board_id = models.CharField(max_length=250)
    start_columns_str = models.CharField(max_length=250, blank=True, null = True)
    end_columns_str = models.CharField(max_length=250, blank=True, null = True)
    trello_user_key = models.CharField(max_length=250)
    trello_user_token = models.CharField(max_length=250)


    def get_throughput(self):
        cards = []
        data = {}
        today_week = datetime.today().isocalendar()[1]
    
        for card in self.card_set.all():
            end_date = card.end_date
            if end_date!="":
                week = end_date.isocalendar()[1]
                if week not in data:
                    data[week] = 1
                else:
                    data[week] += 1
        i = min(data.keys())
        while i<=today_week:
            if i not in data: data[week] = 0
            i+=1
        tp_median = numpy.median(list(data.values()))
        tp_mean = numpy.mean(list(data.values()))
        return [data, tp_median, tp_mean]
    
    def get_cfd(self):
        for card in self.card_set.all():
            pass
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Label(models.Model):
    name = models.CharField(max_length=250)
    label_id = models.CharField(max_length=250, unique=True)
    color = models.CharField(max_length=200, null=True, blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

LEADTIME_CHOICES = (
        ("Start", "Pode representar o início do Leadtime"),
        ("End", "Pode representar o fim do Leadtime"),
        ("None", "Não considerar nem como início nem fim")
)

class Column(models.Model):
    name = models.CharField(max_length=250)
    column_id = models.CharField(max_length=250, unique=True)
    active = models.BooleanField(default=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE) 
    importance_order = models.IntegerField(default=1000)
    leadtime_period = models.CharField(
            max_length=5,
            choices = LEADTIME_CHOICES,
            default = "None",
        )
       
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]


class Card(models.Model):
    card_id = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    choice_text = models.CharField(max_length=200)
    labels = models.ManyToManyField(Label)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    @property
    def end_date(self):
        end_columns = self.board.column_set.filter(leadtime_period="End").order_by('importance_order')
        end_date = ""
        for transaction in self.transaction_set.all():
            for end_column in end_columns:
                if end_date=="" and transaction.column==end_column:
                    end_date = transaction.date
                    end_columns = []
        return end_date

    @property
    def start_date(self):
 
        start_columns = self.board.column_set.filter(leadtime_period="Start").order_by('importance_order')
        start_date = ""
        for transaction in self.transaction_set.all():
            for start_column in start_columns:
                if start_date=="" and transaction.column==start_column:
                    start_date = transaction.date
                    start_columns = []
        return start_date

    def get_leadtime(self):
        end_date = self.end_date
        start_date = self.start_date
        if end_date !="" and start_date!="":
            leadtime_delta = end_date-start_date
            return leadtime_delta.days
        else:
            return None


class Transaction(models.Model):
    date = models.DateTimeField()
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('column', 'date',)
