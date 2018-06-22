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


    def add_arguments(self, parser):
        parser.add_argument(
        '--board',
            action='store',
            dest='board',
            type=str,
            default="",
            help='Import the board with this id',
        )



    def save_leadtime(self, board):
        for card in board.card_set.all():
            leadtime = card.get_leadtime()
            if leadtime is not None and leadtime>=0:
                try:
                    leadtime_chart = models.ChartLeadtime.objects.get(card=card)
                except models.ChartLeadtime.DoesNotExist:
                    leadtime_chart = models.ChartLeadtime()
                    leadtime_chart.card = card
                leadtime_chart.end_date = card.end_date
                leadtime_chart.leadtime = leadtime
                leadtime_chart.save()


    def save_throughput(self, board):
        throughput_graph = []
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

            week_values=""
            for type in models.CARD_TYPE_CHOICES:
                line.append(data[week_index][type[0]])

            tp_obj.data = json.dumps(line)
            tp_obj.save()


    def save_cfd_data(self, board):
         number_of_days = 220
         date_starter = timezone.now() - datetime.timedelta(days=number_of_days)
         columns = board.column_set.all().order_by('-board_position')
         cfd_hash = {}
         class EndColumn: name = "Done"
         cards_done = []

         bla = 0
         while date_starter.date() <= datetime.date.today():
             cfd_hash[date_starter.date()]= {}

             for column in columns:

                 transactions = column.transaction_set.filter(
                         Q(date__date__lte=date_starter),
                         Q(end_date_cache__gt=date_starter) | Q(end_date_cache__isnull=True))
                 if column.leadtime_period=="End":
                     column = EndColumn
                 if column.name not in cfd_hash[date_starter.date()]:
                     cfd_hash[date_starter.date()][column.name]=[]
                 for transaction in transactions:
                     if (date_starter.date() >=
                                     transaction.date.date() and
                                     date_starter.date() <
                                     transaction.end_date.date()):
                         cfd_hash[date_starter.date()][column.name].append(transaction.card.id)
                         if column.name=="Done":
                             cards_done.append(transaction.card.id)

                     else:
                         bla+=1
 
             date_starter+=datetime.timedelta(days=1)
         print(bla)
         cfd_header = ['Dia']
 
         cfd_list = [cfd_header]
         done_start = 0
         for day in cfd_hash.keys():
             cfd_day_list = [str(day)]
             end_column_filled = False
             column_totals={}
             for column in columns:
                 if not (column.leadtime_period=="End" and end_column_filled == True) and column.active:
                     if column.leadtime_period=="End":
                         column = EndColumn
                         end_column_filled = True
                         total = len(cfd_hash[day][column.name])
                         total = total-done_start
                     else:
                         total = len(cfd_hash[day][column.name])
                     if column.name not in cfd_header:
                         cfd_header.append(column.name)
                         cfd_list[0] = cfd_header
                     if column.name not in column_totals.keys():
                         column_totals[column.name]=0
                     column_totals[column.name]+=total
             for total in column_totals.values():
                cfd_day_list.append(total)
              
             cfd_list.append(cfd_day_list)
             if len(cfd_list)==2:
                 done_index = cfd_list[0].index('Done')
                 done_start=cfd_day_list[done_index]
                 cfd_list[1][done_index]=0
         try:
             cfdObj = board.chartcfd
         except ObjectDoesNotExist:
             cfdObj = models.ChartCFD()
             cfdObj.board = board
         cfdObj.chart_columns = json.dumps(cfd_header)
         cfdObj.save() 
         header = cfd_list.pop(0)
         cfd_day_list = []
         cfdObj.chartcfddata_set.all().delete()
         for data in cfd_list:
            cfd_day = models.ChartCFDData()
            cfd_day.day = data[0]
            cfd_day.data = json.dumps(data)
            cfd_day_list.append(cfd_day)
            cfd_day.chartcfd = cfdObj
            cfd_day.save()
         cfdObj.save()
 

    def handle(self, *args, **options):

        if options['board'] != "":
            boards = models.Board.objects.filter(board_id=options['board'])
        else:
            boards = models.Board.objects.all()

        for board in boards:
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
