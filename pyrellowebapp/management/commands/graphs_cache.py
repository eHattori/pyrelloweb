from django.core.management.base import BaseCommand, CommandError
from pyrellowebapp import models
import datetime
import json
import requests
import numpy

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
        leadtime_graph += "]"
        leadtime_data = [leadtime_graph, "%.2f" % round(numpy.percentile(percentil_leadtime, 90),2)]

        try:
            graphdata = board.graphdata_set.get(graph="Leadtime")
        except Exception as e:
            graphdata = models.GraphData()
            graphdata.board = board
        graphdata.graph = "Leadtime"
        graphdata.data = leadtime_data
        graphdata.save()


    def save_cfd_data(self, board):
         number_of_days = 90
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
 
         try:
             graphdata = board.graphdata_set.get(graph="CFD")

         except Exception as e:
             print(e)
             graphdata = models.GraphData()
             graphdata.board = board
         graphdata.graph = "CFD"
         graphdata.data =cfd_list
         graphdata.save()


    def handle(self, *args, **options):

        if options['board'] != "":
            boards = models.Board.objects.filter(board_id=options['board'])
        else:
            boards = models.Board.objects.all()

        for board in boards:
            try:
                print("Leadtime - %s" % board.name)
                self.save_leadtime(board)
                print("CFD - %s" % board.name)
                self.save_cfd_data(board)
            except Exception as e:
                print("GRAPHS CACHE - %s Error: %s" % (board.name, e))
        print("Done")
