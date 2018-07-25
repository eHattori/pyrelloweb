from django import template
import datetime
from pyrellowebapp.models import Board
from pyrellowebapp import models
import json
from django.db.models import Q
import numpy
import os
from django.db.models import Avg, Max, Min, Sum

register = template.Library()

VALUE_TYPE_INDEX = 1
BUG_TYPE_INDEX = 2
IMPROVEMENT_TYPE_INDEX = 3
OPS_TYPE_INDEX = 4
OTHERS_TYPE_INDEX = 5
SATURDAY = 5
DEFAULT_NUMBER_OF_DAYS = 60
PERCENTILE_CONFIG = os.environ.get('PERCENTILE', 80)
DEFAULT_START_DATE = datetime.date.today() - datetime.timedelta(days=DEFAULT_NUMBER_OF_DAYS)
DEFAULT_END_DATE = datetime.date.today()
SERVICE_CLASS_OPTIONS = {}
for key, value in models.LABEL_SERVICE_CLASS:
    SERVICE_CLASS_OPTIONS[key]=value

def get_start_date(request):
    start_date = request.POST.get('start_date', str(DEFAULT_START_DATE))
    start_date = start_date.split("-")
    start_date = datetime.date(int(start_date[0]),int(start_date[1]),int(start_date[2]))
 
    return start_date


def get_end_date(request):
    end_date = request.POST.get('end_date', str(datetime.date.today()))
    end_date = end_date.split("-")
    end_date = datetime.date(int(end_date[0]),int(end_date[1]),int(end_date[2]))
 
    return end_date


@register.simple_tag
def menu():
    boards = Board.objects.all()
    result = []
    for board in boards:
        menu_item = {"menu": board.name, "link": "?db_board_id=%s" % board.id}
        result.append(menu_item)
    return result


@register.simple_tag
def page(request):
    db_board_id = request.GET.get('db_board_id', None)
    service_class_filter = request.POST.get('service_class', "standard")
    start_date = get_start_date(request)
    end_date = get_end_date(request)
    result = {}
    result['start_date'] = start_date
    result['end_date'] = end_date
    result['title'] = "Início"
    if db_board_id:
        board = Board.objects.get(id=db_board_id)
        result['db_board_id'] = board.id
        result['service_class'] = service_class_filter
        result['service_class_text'] = SERVICE_CLASS_OPTIONS[service_class_filter]
        result['title'] = board.name
    return result
 
 
@register.simple_tag
def histogram(request):
    db_board_id = request.GET.get('db_board_id', None)
    graph = []
    if db_board_id:
        board = Board.objects.get(db_board_id)
        try:
            graph = board.graphdata_set.get(graph="Histogram").data
            graph = json.loads(graph)
        except Exception as e:
            pass 
    return graph



@register.simple_tag
def leadtime(request):
    db_board_id = request.GET.get('db_board_id', None)
    if db_board_id:
        board = Board.objects.get(id=db_board_id)
        start_date = get_start_date(request)
        end_date = get_end_date(request)
        service_class_filter = request.POST.get('service_class', "standard")
        try:
            leadtime = models.ChartLeadtime.objects.filter(
                service_class=service_class_filter,
                card__board=board,
                end_date__range=(start_date, end_date)).order_by('end_date')

            leadtime_max = models.ChartLeadtime.objects.filter(
                service_class=service_class_filter,
                card__board=board,
                end_date__range=(start_date, end_date)).order_by('end_date').aggregate(Max('leadtime'))
            
            max_vAxis = 50
            if leadtime_max['leadtime__max']!=None and leadtime_max['leadtime__max']<50:
                max_vAxis = leadtime_max['leadtime__max']

            leadtime_value = models.ChartLeadtime.objects.filter(
                card_type="value",
                card__board=board,
                end_date__range=(start_date, end_date)).order_by('end_date')

            total_items = []
            for item in leadtime_value:
                total_items.append(item.leadtime)

            try:
                value_percentile = "%.1f" % round(numpy.percentile(total_items, PERCENTILE_CONFIG),2)
            except:
                value_percentile = "-"
            result = {
                'percentile_config' : PERCENTILE_CONFIG,
                'value_percentile' : value_percentile,
                'cards': leadtime,
                'max_vAxis': max_vAxis}
            return result
        except Exception as e:
            print("error leadtime  %s" % e)
    return None


@register.simple_tag
def throughput(request):
    db_board_id = request.GET.get('db_board_id', None)

    chart = []
    type_list = list(models.CARD_TYPE_CHOICES)
    result = {'labels': type_list, 'mean_general': '-', 'mean_value': '-',
            'defectload': '-'}
    if db_board_id:
        board = Board.objects.get(id=db_board_id)
        try:
            start_date = get_start_date(request)
            end_date = get_end_date(request)
            end_week_day = end_date.weekday()
            start_week = start_date.isocalendar()[1] 
            start_year = start_date.isocalendar()[0]
            end_week =  end_date.isocalendar()[1]
            end_year = end_date.isocalendar()[0]

            ignore_date = datetime.date.today()
            ignore_week = ignore_date.isocalendar()[1]
            ignore_year = ignore_date.isocalendar()[0]
            ignore_week_day = ignore_date.weekday()

            if ignore_week_day < SATURDAY:
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
                            total_tp_week+=value

                    total_tp_value_week_list.append(data[VALUE_TYPE_INDEX])
                    total_tp_week_list.append(total_tp_week) 

                total_bug += data[BUG_TYPE_INDEX]
                total_value += data[VALUE_TYPE_INDEX]
                total_ops += data[OPS_TYPE_INDEX]
                total_improvement += data[IMPROVEMENT_TYPE_INDEX]

            total_tp += total_bug+total_value+total_ops+total_improvement
            try:
                result['mean_value'] = "%.1f" % (numpy.mean(total_tp_value_week_list))
            except:
                result['mean_value'] = "-"
            try:
                result['mean_general'] = "%.1f" % (numpy.mean(total_tp_week_list))
            except:
                result['mean_general'] = "-"
            try:
                result['defectload'] = "%.1f" % ((total_bug*100)/total_tp)
            except:
                result['defectload'] = "-"
                
            result['type_totals'] = [
                ['Tipo de cartão', 'Total de entregas'],
                ['Bug', total_bug],
                ['Valor', total_value],
                ['Melhorias', total_improvement],
                ['Ops', total_ops],
            ]
            result['data'] = chart
        except Exception as e:
            print(e) 
    return result


@register.simple_tag
def cfd(request):
    db_board_id = request.GET.get('db_board_id', None)
    start_date = get_start_date(request)
    end_date = get_end_date(request)
    cfd_graph = []
    if db_board_id:
        board = Board.objects.get(id=db_board_id)
        try:
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
