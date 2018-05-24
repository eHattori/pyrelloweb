
from django import template

from pyrellowebapp.models import Board

register = template.Library()


@register.simple_tag
def graphics_one():
    testando = Board.objects.all()
    return {
        'chave_1': testando,
    }
