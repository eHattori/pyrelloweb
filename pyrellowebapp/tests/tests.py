# coding:utf-8
from django.test import TestCase
from pyrellowebapp.management.commands import graphs_cache
from pyrellowebapp import models
class TestGraphsChart(TestCase):
    def test_normal_flow(self):
        gc = graphs_cache.Command()
        board = models.Board.objects.all()[0]
        
        gc.save_cfd_data(board)

