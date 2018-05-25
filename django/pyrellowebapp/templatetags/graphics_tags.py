
from django import template

from pyrellowebapp.models import Board
import numpy
register = template.Library()


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
            leadtime = card.get_leadtime()
            if leadtime is not None:
                histogram.append(['card', card.get_leadtime()])
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
    leadtime_graph = None
    if board_id:
        board = Board.objects.get(board_id=board_id)
        leadtime_graph = []
        i = 0
        percentil_leadtime = []
        for card in board.card_set.all():
            leadtime = card.get_leadtime()
            if leadtime is not None:
                i += 1
                percentil_leadtime.append(leadtime)
                leadtime_graph.append([i, leadtime])
        return [leadtime_graph, "%.2f" % round(numpy.percentile(percentil_leadtime, 90),2)]
    return []

@register.simple_tag
def throughput(request):
    board_id = request.GET.get('board_id', None)
    throughput_graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        data, median, mean = board.get_throughput()
        for week in data.keys():
            throughput_graph.append([week, data[week]])
        return [throughput_graph, "%.2f" % round(median,2), "%.2f" % round(mean,2)]
    return []

@register.simple_tag
def cfd(request):
    board_id = request.GET.get('board_id', None)
    cfd_graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        data = board.get_cfd()
 
    return cfd_graph
