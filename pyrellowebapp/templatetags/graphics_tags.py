from django import template
from pyrellowebapp.models import Board
from pyrellowebapp import models

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
    histogram = None
    if board_id:
        board = Board.objects.get(board_id=board_id)
        histogram = []
        for card in board.card_set.all():
            if card.card_id not in cache.keys():
                cache[card.card_id]=card.get_leadtime()
            leadtime = cache[card.card_id]
            if leadtime is not None and leadtime>=0:
                histogram.append(['card', leadtime])
    return histogram


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
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            graph = board.graphdata_set.get(graph="Leadtime").data
            graph = eval(graph)
        except Exception as e:
            graph = []
 
    return graph


@register.simple_tag
def throughput(request):
    board_id = request.GET.get('board_id', None)
    throughput_graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        #TODO desfazer esse cache pq prende o board
        cache={}
        if board.board_id not in cache.keys():
            cache[board.board_id] = board.get_throughput()

        labels, data, median, mean = cache[board.board_id].values()
        line = ""
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
            week_values=""
            for type in models.CARD_TYPE_CHOICES:
                week_values += "%s," % data[week_index][type[0]]
            line += "[ '%s', %s],"  % ( week_index, week_values)
        throughput_graph = "[%s]" % line
        result = { 
                'labels': labels,
                'data': throughput_graph,
                'median': round(median,2),
                'mean':  "%.2f" % round(mean,2)
                }
        return result
    return {}

@register.simple_tag
def cfd(request):
    board_id = request.GET.get('board_id', None)
    cfd_graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            cfd_graph = board.graphdata_set.get(graph="CFD").data
        except Exception as e:
            print(e)
            cfd_graph = []
 
    return cfd_graph
