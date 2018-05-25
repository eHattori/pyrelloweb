
from django import template

from pyrellowebapp.models import Board

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
def leadtime(request):
    board_id = request.GET.get('board_id', None)
    leadtime_graph = None
    if board_id:
        board = Board.objects.get(board_id=board_id)
        leadtime_graph = []
        i = 0
        for card in board.card_set.all():
            leadtime = card.get_leadtime()
            if leadtime is not None:
                i += 1
                leadtime_graph.append([i, card.get_leadtime()])
    return leadtime_graph
