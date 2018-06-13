from django import template
import datetime
from pyrellowebapp.models import Board
from pyrellowebapp import models
import json

register = template.Library()
cache={}

@register.simple_tag
def menu():
    boards = Board.objects.all()
    result = []
    for board in boards:
        menu_item = {"menu": board.name, "link": "?board_id=%s" % board.board_id}
        result.append(menu_item)
    return result


@register.simple_tag
def histogram(request):
    board_id = request.GET.get('board_id', None)
    graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            graph = board.graphdata_set.get(graph="Histogram").data
            graph = json.loads(graph)
        except Exception as e:
            pass 
    return graph


@register.simple_tag
def page_title(request):
    board_id = request.GET.get('board_id', None)
    if board_id:
        board = Board.objects.get(board_id=board_id)
        return board.name
    return "Início"
 
 
@register.simple_tag
def leadtime(request):
    board_id = request.GET.get('board_id', None)
    graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            graph = board.graphdata_set.get(graph="Leadtime").data
            graph = json.loads(graph)
        except Exception as e:
            pass 
    return graph


@register.simple_tag
def throughput(request):
    board_id = request.GET.get('board_id', None)
    graph = {}
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            graph = board.graphdata_set.get(graph="Throughput").data
            graph = json.loads(graph)
        except Exception as e:
            pass 
    return graph


@register.simple_tag
def cfd(request):
    board_id = request.GET.get('board_id', None)
    number_of_days = int(request.GET.get('number_of_days', 60))
    cfd_graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            start_date = datetime.date.today() - datetime.timedelta(days=number_of_days)
            end_date = datetime.date.today()

            cfd_graph_data = board.chartcfd.chartcfddata_set.filter(
                    day__range=(start_date, end_date))
            chart_columns = json.loads(board.chartcfd.chart_columns)
            cfd_graph.append(chart_columns)
            i=0
            for data in cfd_graph_data:
                done_index = chart_columns.index('Done')
                data = json.loads(data.data)
                if i == 0:
                    done_start = data[done_index] 
                    i += 1
                data[done_index]-=done_start
                cfd_graph.append(data)

        except Exception as e:
            print(e)
            cfd_graph = []
 
    return cfd_graph
