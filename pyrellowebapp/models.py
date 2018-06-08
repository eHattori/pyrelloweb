from django.db import models
import datetime
import numpy
from pprint import pprint

CARD_TYPE_CHOICES = (
        ("value","Valor"),
        ("bug","Bug"),
        ("improvement","Melhorias"),
        ("ops","Ops"),
        ("others","Outros")
        )
BOARD_TYPE_CHOICES = (
        ("trello", "Trello"),
        ("jira", "Jira"),
        )

class Board(models.Model):
    name = models.CharField(max_length=250)
    board_id = models.CharField(max_length=250)
    trello_user_key = models.CharField(max_length=250)
    trello_user_token = models.CharField(max_length=250)
    board_type = models.CharField(
            choices = BOARD_TYPE_CHOICES,
            max_length=30,
            default = "none")
 
    jira_server_url = models.CharField(max_length=250, null=True, blank=True)
    
    def get_throughput(self):
        cards = []
        data = {}
        week_total = {}
        today_week = datetime.datetime.today().isocalendar()[1]
    
        for card in self.card_set.all():
            end_date = card.end_date
            if end_date!="":
                week = "%s-%s" % (end_date.isocalendar()[1], end_date.isocalendar()[0])
                if week not in data:
                    data[week] = {card.type : 1}
                    week_total[week] = 1

                else:
                    if card.type in data[week]:
                        data[week][card.type] += 1
                    else:
                        data[week][card.type] = 1
                    week_total[week] += 1
        year_list = {}

        for week in data.keys():
            week, year = week.split('-')
            if year not in year_list:
                year_list[year]=[]
            year_list[year].append(int(week))

        for year in year_list.keys():
            week = min(year_list[year])
            last_week = today_week
            if int(year)<datetime.datetime.today().isocalendar()[0]:
                last_week = datetime.date(int(year), 12, 28).isocalendar()[1]
            while week<=last_week:
                week_key = "%s-%s" % (week, year)
                if week_key not in data:
                    data[week_key] = {}
                
                for type in CARD_TYPE_CHOICES:
                    if type[0] not in data[week_key]:
                        data[week_key][type[0]]=0
                    
                week+=1

        tp_median = numpy.median(list(week_total.values()))
        tp_mean = numpy.mean(list(week_total.values()))
        result = { 
                'labels': CARD_TYPE_CHOICES,
                'data': data,
                'median': tp_median,
                'mean': tp_mean
                }
        return result
    

    def get_cfd(self):
        date_starter = datetime.date.today() - datetime.timedelta(days=30)
        columns = self.column_set.all().order_by('-board_position')
        cfd_hash = {}
        class EndColumn: name = "Done"
        cards_done = []
        while date_starter <= datetime.date.today():
            cfd_hash[date_starter]= {}
            for column in columns:

                transactions = column.transaction_set.all()
                if column.leadtime_period=="End":
                    column = EndColumn
                if column not in cfd_hash[date_starter]:
                    cfd_hash[date_starter][column]=[]

                for transaction in transactions:
                    end_date = transaction.end_date
                    if (transaction.card.id in cards_done and
                            column.name=="Done") or (date_starter >=
                                    transaction.date.date() and date_starter <
                                    end_date.date() and
                                    transaction.date.date()!=end_date.date()):
                        cfd_hash[date_starter][column].append(transaction.card.id)

                        if column.name=="Done":
                            cards_done.append(transaction.card.id)
            date_starter+=datetime.timedelta(days=1)
        cfd_header = ['Dia']

        cfd_list = [cfd_header]
        done_start = 0
        for day in cfd_hash.keys():
            cfd_day_list = [str(day)]
            end_column_filled = False
            for column in columns:
                if not (column.leadtime_period=="End" and end_column_filled == True) and column.active:
                    if column.leadtime_period=="End":
                        column = EndColumn
                        end_column_filled = True
                        total = len(cfd_hash[day][column])
                        total = total-done_start
                    else:
                        total = len(cfd_hash[day][column])
                    if column.name not in cfd_header:
                        cfd_header.append(column.name)
                        cfd_list[0] = cfd_header
                    cfd_day_list.append(total)

            cfd_list.append(cfd_day_list)
            if len(cfd_list)==2:
                done_index = cfd_list[0].index('Done')
                done_start=cfd_day_list[done_index]
                cfd_list[1][done_index]=0

        return cfd_list

    
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
                    return  end_date
        return end_date

    @property
    def type(self):
        if self.labels:
            for label in self.labels.exclude(card_type="others"):
                if label.card_type!="others":
                    return label.card_type
        return "others"

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
            return datetime.datetime.today()+datetime.timedelta(days=1)


GRAPH_CHOICES = (
        ("Leadtime", "Leadtime"),
        ("Throughput", "Throughput"),
        ("CFD", "CFD"),
        ("Histogram", "Leadtime Histogram"),
        ("90Percentil", "90 Percentil Leadtime"),
        ("ThroughputMean", "Média Throughput"),
        ("ThroughputMedian", "Mediana Throughput"),

)
class GraphData(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    graph = models.CharField(
            max_length=100,
            choices=GRAPH_CHOICES,
    )
    data = models.TextField()

