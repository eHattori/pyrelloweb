from django.shortcuts import render

def menu(reqeust, board_id):
    return HTTPResponse("you're looking at board %s." % board_id)
