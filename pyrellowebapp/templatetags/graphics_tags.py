from django import template
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
    cfd_graph = []
    if board_id:
        board = Board.objects.get(board_id=board_id)
        try:
            cfd_graph = board.graphdata_set.get(graph="CFD").data
        except Exception as e:
            print(e)
            cfd_graph = []
 
    return cfd_graph
