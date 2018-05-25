from django.db import models
import datetime

import numpy

from pprint import pprint
class Board(models.Model):
    name = models.CharField(max_length=250)
    board_id = models.CharField(max_length=250)
    trello_user_key = models.CharField(max_length=250)
    trello_user_token = models.CharField(max_length=250)
    
    def get_throughput(self):
        cards = []
        data = {}
        today_week = datetime.datetime.today().isocalendar()[1]
    
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
        date_starter = datetime.datetime.today() - datetime.timedelta(days=30)
        import pytz
        utc=pytz.UTC
        date_starter = utc.localize(date_starter)
        columns = self.column_set.all()
        cfd_hash = {}
        while date_starter <= datetime.datetime.today().replace(tzinfo=utc):
            cfd_hash[date_starter]= {}
            for column in columns:
                cfd_hash[date_starter][column]=[]
                for transaction in column.transaction_set.all():
                    end_date = transaction.end_date
                    if date_starter >= transaction.date.replace(tzinfo=utc) and date_starter <= end_date.replace(tzinfo=utc):
                        cfd_hash[date_starter][column].append(transaction.card.id)
            date_starter+=datetime.timedelta(days=1)
            date_starter.replace(tzinfo=utc)
            

        pprint(cfd_hash)

        for card in self.card_set.all():
            pass
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

LABEL_SERVICE_CLASS = (
        ("expedite", "Expedite"),
        ("standart", "Tarefa padrão"),
        ("fixed", "Data fixa"),
        ("intangible", "Intangível"),
        ("none", "Não é classe de serviço")
        )

CARD_TYPE_CHOICES = (
        ("bug","Bug"),
        ("value","Valor"),
        ("improvement","Melhorias"),
        ("ops","Ops"),
        ("others","Outros")
        )
class Label(models.Model):
    name = models.CharField(max_length=250)
    label_id = models.CharField(max_length=250, unique=True)
    color = models.CharField(max_length=200, null=True, blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    service_class = models.CharField(
            choices = LABEL_SERVICE_CLASS,
            max_length=30,
            default = "none")
    card_type = models.CharField(
            choices = CARD_TYPE_CHOICES,
            max_length=40,
            default="others")
    def __str__(self):
        return self.name
 

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
    board_position = models.FloatField(default=0)
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

    @property
    def end_date(self):
        result = Transaction.objects.filter(card__id=self.card.id).filter(
                date__gt=self.date).order_by('date')
        try:
            return result[0].date
        except:
            return datetime.datetime.today()
