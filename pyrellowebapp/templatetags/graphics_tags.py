from django import template
import datetime
from pyrellowebapp.models import Board
from pyrellowebapp import models
import json
from django.db.models import Q
import numpy

register = template.Library()

VALUE_TYPE_INDEX = 1
BUG_TYPE_INDEX = 2
IMPROVEMENT_TYPE_INDEX = 3
OPS_TYPE_INDEX = 4
OTHERS_TYPE_INDEX = 5
SATURDAY = 5
DEFAULT_NUMBER_OF_DAYS = 60

@register.simple_tag
def menu():
    boards = Board.objects.all()
    result = []
    for board in boards:
        menu_item = {"menu": board.name, "link": "?board_id=%s" % board.board_id}
        result.append(menu_item)
    return result

@register.simple_tag
def page(request):
    board_id = request.GET.get('board_id', None)
    number_of_days = request.GET.get('number_of_days', DEFAULT_NUMBER_OF_DAYS)
    result = {}
    result['number_of_days'] = number_of_days
    result['title'] = "Início"
    if board_id:
        board = Board.objects.get(board_id=board_id)
        result['board_id'] = board.board_id
        result['title'] = board.name
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
def leadtime(request):
    board_id = request.GET.get('board_id', None)
    number_of_days = int(request.GET.get('number_of_days',
        DEFAULT_NUMBER_OF_DAYS))
    if board_id:
        board = Board.objects.get(board_id=board_id)
        start_date = datetime.date.today() - datetime.timedelta(days=number_of_days)
        end_date = datetime.date.today()
        try:
            leadtime = models.ChartLeadtime.objects.filter(card__board=board,
                    end_date__range=(start_date, end_date)).order_by('end_date')
            total_items = []
            for item in leadtime:
                total_items.append(item.leadtime)
            percentile = "%.1f" % round(numpy.percentile(total_items, 90),2)
            result = {'percentile' : percentile,
                    'cards': leadtime}
            return result
        except Exception as e:
            print("error leadtime  %s" % e)
    return None

@register.simple_tag
def throughput(request):
    board_id = request.GET.get('board_id', None)
    number_of_days = int(request.GET.get('number_of_days',
        DEFAULT_NUMBER_OF_DAYS))

    chart = []
    result = {'labels': models.CARD_TYPE_CHOICES, 'mean_general': '-', 'mean_value': '-',
            'defectload': '-'}
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            start_date = datetime.date.today() - datetime.timedelta(days=number_of_days)
            end_date = datetime.date.today()
            end_week_day = end_date.weekday()
            start_week = start_date.isocalendar()[1] 
            start_year = start_date.isocalendar()[0]
            end_week =  end_date.isocalendar()[1]
            end_year = end_date.isocalendar()[0]

            if end_week_day < SATURDAY:
                ignore = "%s-%s" % (end_week, end_year)
            else:
                ignore = False
            if start_year != end_year:
                filter = (Q(year=end_year, week__lte=end_week)
                        | Q(year=start_year, week__gte=start_week))
            else:
                filter = Q(year=start_year, week__range=(start_week, end_week))
            tp_list = board.chartthroughput_set.filter(filter)

            total_tp = 0
            total_bug = 0
            total_value = 0
            total_ops = 0
            total_improvement = 0
            total_others = 0

            total_tp_value_week_list = []
            total_tp_week_list = []
            for tp_obj in tp_list:
                data = json.loads(tp_obj.data)
                chart.append(data)
                total_tp_week = 0
                week = data[0]
                if week != ignore:
                    for counter, value in enumerate(data):
                        if counter!=0:
                            total_tp+=value
                            total_tp_week+=value

                    total_bug += data[BUG_TYPE_INDEX]
                    total_value += data[VALUE_TYPE_INDEX]
                    total_ops += data[OPS_TYPE_INDEX]
                    total_improvement += data[IMPROVEMENT_TYPE_INDEX]
                    total_others += data[OTHERS_TYPE_INDEX]
                    total_tp_value_week_list.append(data[VALUE_TYPE_INDEX])
                    total_tp_week_list.append(total_tp_week) 
            result['mean_value'] = "%.1f" % round(numpy.mean(total_tp_value_week_list))
            result['mean_general'] = "%.1f" % round(numpy.mean(total_tp_week_list))
            result['defectload'] = "%.1f" % round((total_bug*100)/total_tp)
            result['type_totals'] = [
                ['Tipo de cartão', 'Total de entregas'],
                ['Bug', total_bug],
                ['Valor', total_value],
                ['Melhorias', total_improvement],
                ['Ops', total_ops],
                ['Outros', total_others]
            ]
            result['data'] = chart
        except Exception as e:
            print(e) 
    return result


@register.simple_tag
def cfd(request):
    board_id = request.GET.get('board_id', None)
    number_of_days = int(request.GET.get('number_of_days',
        DEFAULT_NUMBER_OF_DAYS))
    cfd_graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            start_date = datetime.date.today() - datetime.timedelta(days=number_of_days)
            end_date = datetime.date.today()

            cfd_graph_data = board.chartcfd.chartcfddata_set.filter(
                    day__range=(start_date, end_date)).order_by('day')
            chart_columns = json.loads(board.chartcfd.chart_columns)
            cfd_graph.append(chart_columns)
            done_start = ""

            for cfd in cfd_graph_data:
                data = json.loads(cfd.data)
                if done_start == "":
                    done_start = len(data['Done'])
                    
                cfd_line = [str(cfd.day)]
                for column in chart_columns:
                    if column != 'Day':
                        if column not in data:
                            value = 0
                        else:
                            if column=='Done':
                                value = len(data[column]) - done_start

                            else:
                                value = len(data[column])
                        cfd_line.append(value)
                cfd_graph.append(cfd_line)

        except Exception as e:
            print(e)
            cfd_graph = [e]
 
    return cfd_graph
