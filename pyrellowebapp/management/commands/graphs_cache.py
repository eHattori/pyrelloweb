from django.core.management.base import BaseCommand, CommandError
from pyrellowebapp import models
import datetime
import json
import requests
import numpy
from django.core.exceptions import ObjectDoesNotExist

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


    def save_histogram(self, board):
        histogram = [['card', 'leadtime']]
        for card in board.card_set.all():
            leadtime =card.get_leadtime()
            if leadtime is not None and leadtime>=0:
                histogram.append([card.name[:60].replace("'", ""), leadtime])
        try:
            graphdata = board.graphdata_set.get(graph="Histogram")
        except Exception as e:
            graphdata = models.GraphData()
            graphdata.board = board
        graphdata.graph = "Histogram"
        graphdata.data = json.dumps(histogram)
        graphdata.save()


    def save_leadtime(self, board):
        leadtime_graph = None
        leadtime_graph = "["
        i = 0
        percentil_leadtime = []
        for card in board.card_set.all():
            leadtime = card.get_leadtime()
            if leadtime is not None and leadtime>=0:
                i += 1
                percentil_leadtime.append(leadtime)
                leadtime_graph+="[{v:%s, f:'%s days'}, {v:%s, f:'%s...'}]," % (i,
                        leadtime ,leadtime, card.name[:60].replace("'", ""))
        if len(percentil_leadtime)>0:
            leadtime_graph += "]"
            leadtime_data = [leadtime_graph, "%.2f" % round(numpy.percentile(percentil_leadtime, 90),2)]

            try:
                graphdata = board.graphdata_set.get(graph="Leadtime")
            except Exception as e:
                graphdata = models.GraphData()
                graphdata.board = board
            graphdata.graph = "Leadtime"
            graphdata.data = json.dumps(leadtime_data)
            graphdata.save()

    def save_throughput(self, board):
        throughput_graph = []
        throughput_data = board.get_throughput()

        labels, data, median, mean = throughput_data.values()
        line = ""
        sorted_data = []
        for week_index in data.keys():
            week, year = week_index.split("-")

            if len(week)==1:
                week="0%s" % week

            sorted_data.append(float("%s.%s"% (year, week)))
        sorted_data.sort()
        total_value = 0
        total_defect = 0
        total_throughput = 0
        for week_index in sorted_data:
            year, week = str(week_index).split(".")
            if len(week)==1:
                week="%s0" % week
            week_index="%s-%s" % (int(week), year)
            week_values=""
            for type in models.CARD_TYPE_CHOICES:
                week_values += "%s," % data[week_index][type[0]]
                total_throughput += data[week_index][type[0]]
                if type[0] == "value":
                    total_value += data[week_index][type[0]]
                elif type[0] == "bug":
                    total_defect += data[week_index][type[0]]

            line += "[ '%s', %s],"  % ( week_index, week_values)
        throughput_graph = "[%s]" % line
        valueload = (total_value*100)/total_throughput
        defectload = (total_defect*100)/total_throughput
        result = { 
                'labels': labels,
                'data': throughput_graph,
                'median': "%.2f" % round(median,2),
                'mean':  "%.2f" % round(mean,2),
                'valueload': "%.2f" % valueload,
                'defectload': "%.2f" % defectload,
                }
        try:
            graphdata = board.graphdata_set.get(graph="Throughput")
        except Exception as e:
            graphdata = models.GraphData()
            graphdata.board = board
        graphdata.graph = "Throughput"
        graphdata.data = json.dumps(result)
        graphdata.save()


    def save_cfd_data(self, board):
         number_of_days = 120
         date_starter = datetime.date.today() - datetime.timedelta(days=number_of_days)
         columns = board.column_set.all().order_by('-board_position')
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
                     if (date_starter >=
                                     transaction.date.date() and date_starter <
                                     transaction.end_date.date()):
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
            print (data)
         cfdObj.save()
 

    def handle(self, *args, **options):

        if options['board'] != "":
            boards = models.Board.objects.filter(board_id=options['board'])
        else:
            boards = models.Board.objects.all()

        for board in boards:
            try:
                print("Histogram - %s" % board.name)
                self.save_histogram(board)
            except Exception as e:
                print("GRAPHS CACHE - %s Error: %s" % (board.name, e))

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
