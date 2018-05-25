
from django import template

from pyrellowebapp.models import Board

register = template.Library()


@register.simple_tag
def graphics_one():
    testando = Board.objects.all()
    return {
        'chave_1': testando,
    }


@register.simple_tag
def menu():
    boards = Board.objects.all()
    result = []
    GRAPHICS = [{"label": "Histogram", "link": "histogram"}]
    for board in boards:
        menu_item = {"menu": board.name, "submenu": []}
        for graphic in GRAPHICS:

            menu_item["submenu"].append(
                    {'label':  graphic["label"],
                    'link': "boards/%s/%s" % (board.id, graphic["link"])})
        
        result.append(menu_item)
    return result

@register.simple_tag
def histogram():
    board = Board.objects.get(id=1)
    histogram=[]
    for card in board.card_set.all():
        leadtime = card.get_leadtime()
        if leadtime != None:
            histogram.append(['card', card.get_leadtime()])
    return histogram

@register.simple_tag
def leadtime():
    board = Board.objects.get(id=1)
    leadtime_graph=[]
    i=0
    for card in board.card_set.all():
        leadtime = card.get_leadtime()
        if leadtime != None:
            i+=1
            leadtime_graph.append([i, card.get_leadtime()])
    print(leadtime_graph)
    return leadtime_graph
