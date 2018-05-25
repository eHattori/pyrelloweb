
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
    GRAPHICS = [{"label": "Histogram", "link": "boards/1/histogram"}]
    for board in boards:
        menu_item = {"menu": board.name}
        for graphic in GRAPHICS:
            menu_item["label"] = graphic["label"]
            menu_item["link"] = graphic["link"]
        
        result.append(menu_item)

    return result
