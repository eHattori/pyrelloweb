from django.core.management.base import BaseCommand, CommandError
from pyrellowebapp import models
import datetime
import json
import requests
import numpy
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

class Command(BaseCommand):
    local_list_names = {}
    filter_by_label = Q()
    filter_transaction_by_label = Q()

    def add_arguments(self, parser):
        parser.add_argument(
        '--board',
            action='store',
            dest='board',
            type=str,
            default="",
            help='Generate charts for the board with this id',
        )

    def save_leadtime(self, board):
        models.ChartLeadtime.objects.filter(card__board=board).delete()
        for card in board.card_set.filter(self.filter_by_label):
            if card.type != "others":
                leadtime = card.get_leadtime()
                if leadtime is not None and leadtime>=0:
                    try:
                        leadtime_chart = models.ChartLeadtime.objects.get(card=card)
                    except models.ChartLeadtime.DoesNotExist:
                        leadtime_chart = models.ChartLeadtime()
                        leadtime_chart.card = card
                    leadtime_chart.service_class = card.service_class
                    leadtime_chart.card_type = card.type
                    leadtime_chart.end_date = card.end_date
                    leadtime_chart.leadtime = leadtime
                    leadtime_chart.save()


    def save_throughput(self, board):
        throughput_graph = []
        board.chartthroughput_set.all().delete()
        board.save()
        throughput_data = board.get_throughput()

        labels, data = throughput_data.values()
        sorted_data = []
        for week_index in data.keys():
            week, year = week_index.split("-")

            if len(week)==1:
                week="0%s" % week

            sorted_data.append(float("%s.%s"% (year, week)))
        sorted_data.sort()
        for week_index in sorted_data:
            year, week = str(week_index).split(".")
            if len(week)==1:
                week="%s0" % week
            week_index="%s-%s" % (int(week), year)

            line=[week_index]
            try:
                tp_obj = models.ChartThroughput.objects.get(
                        week_label=week_index,
                        board=board)
            except Exception as e:
                tp_obj = models.ChartThroughput()
            tp_obj.week_label=week_index
            tp_obj.week = week
            tp_obj.year = year
            tp_obj.board = board

            for card_type in models.CARD_TYPE_CHOICES:
                type_key_index = 0
                line.append(data[week_index][card_type[type_key_index]])

            tp_obj.data = json.dumps(line)
            tp_obj.save()

    def group_cfd_cards(self, cfd_day, board):
        cfd_hash = {}
        cfd_hash[cfd_day]= {}
        class EndColumn: name = "Done"
        cards_done = []
        columns = board.column_set.filter(Q(active=True) | Q(leadtime_period="End")).order_by('-board_position')

        for column in columns:
            transactions = column.transaction_set.filter(
                     Q(date__date__lte=cfd_day),
                     Q(end_date_cache__date__gt=cfd_day) | Q(end_date_cache__isnull=True),
                     self.filter_transaction_by_label,)
            if column.leadtime_period=="End":
                 column = EndColumn
            if column.name not in cfd_hash[cfd_day]:
                 cfd_hash[cfd_day][column.name]=[]
            for transaction in transactions:
                if (cfd_day >=
                                 transaction.date.date() and
                                 cfd_day <
                                 transaction.end_date.date()):
                    if transaction.card.id not in cfd_hash[cfd_day][column.name]:
                        cfd_hash[cfd_day][column.name].append(transaction.card.id)
                    if column.name=="Done":
                        cards_done.append(transaction.card.id)
        return cfd_hash

    def get_cfd_header(self, board):
        columns = board.column_set.filter(Q(active=True) | Q(leadtime_period="End")).order_by('-board_position')
        header = ['Day']
        for column in columns:
            if column.leadtime_period == 'End':
                column.name = 'Done'
            if column.name not in header:
                header.append(column.name)
        return header

    def save_cfd_data(self, board):
         number_of_days = 120
         date_starter = timezone.now() - datetime.timedelta(days=number_of_days)
         cfd_list = []

         while date_starter.date() <= datetime.date.today():
            cfd_list.append(self.group_cfd_cards(date_starter.date(), board))
            date_starter+=datetime.timedelta(days=1)
         try:
             cfdObj = board.chartcfd
         except ObjectDoesNotExist:
             cfdObj = models.ChartCFD()
             cfdObj.board = board

         cfdObj.chart_columns = json.dumps(self.get_cfd_header(board))
         cfdObj.save()
         cfd_day_list = []
         cfdObj.chartcfddata_set.all().delete()

         for data in cfd_list:
            cfd_day = models.ChartCFDData()
            cfd_day.day = list(data.keys())[0]
            cfd_day.data = json.dumps(data[cfd_day.day])
            cfd_day.chartcfd = cfdObj
            cfd_day.save()
         cfdObj.save()
 

    def handle(self, *args, **options):

        if options['board'] != "":
            boards = models.Board.objects.filter(board_id=options['board'])
        else:
            boards = models.Board.objects.all()

        for board in boards:
            if board.filter_by_label:
                labels = models.Label.objects.filter(name=board.filter_by_label)
                self.filter_by_label = Q(labels__in=labels)
                self.filter_transaction_by_label = Q(card__labels__in= models.Label.objects.filter(name=board.filter_by_label))
            else:
                self.filter_by_label = Q()
                self.filter_transaction_by_label = Q()

            try:
                print("Throughput - %s" % board.name)
                self.save_throughput(board)
            except Exception as e:
                print("GRAPHS CACHE - %s Error: %s" % (board.name, e))

            try:
                print("Leadtime - %s" % board.name)
                self.save_leadtime(board)
            except Exception as e:
                print("GRAPHS CACHE - %s Error: %s" % (board.name, e))

            try:
                print("CFD - %s" % board.name)
                self.save_cfd_data(board)
            except Exception as e:
                print("GRAPHS CACHE - %s Error: %s" % (board.name, e))

        print("Done")
