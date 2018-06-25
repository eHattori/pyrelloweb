# coding:utf-8
from django.test import TestCase
from pyrellowebapp.management.commands import graphs_cache
from pyrellowebapp import models
from django.utils import timezone
import datetime
from pprint import pprint
import json

class TestGraphsChart(TestCase):
    first_transaction = None
    board = None
    card = None

    def setUp(self):
        self.board = models.Board()
        self.board.name="Teste"
        self.board.trello_user_key="teste"
        self.board.trello_user_token="teste"
        self.board.board_id="teste"
        self.board.board_type="trello"
        self.board.save()

        column = models.Column()
        column.board = self.board
        column.board_position=0
        column.column_id="1"
        column.importance_order=0
        column.leadtime_period='Start'
        column.name='ToDo'
        column.save()
        start_column = column

        column = models.Column()
        column.board = self.board
        column.board_position=1
        column.column_id="2"
        column.importance_order=2
        column.leadtime_period='None'
        column.name='Doing'
        column.save()
        doing_column = column

        column = models.Column()
        column.board = self.board
        column.board_position=30
        column.column_id="30"
        column.importance_order=30
        column.leadtime_period='End'
        column.name='Done'
        column.save()
        end_column = column

        card = models.Card()
        card.board = self.board
        card.card_id="1212"
        card.end_date_cache=timezone.now()
        card.name="ika bla"
        card.save()
        self.card = card

        transaction = models.Transaction()
        transaction.card = card
        transaction.column = start_column
        transaction.date = timezone.now()-datetime.timedelta(days=4)
        end_date_cache = None
        transaction.save()
        self.first_transaction = transaction

        transaction = models.Transaction()
        transaction.card = card
        transaction.column = doing_column
        transaction.date = timezone.now()-datetime.timedelta(days=2)
        end_date_cache = None
        transaction.save()

        transaction = models.Transaction()
        transaction.card = card
        transaction.column = end_column
        transaction.date = timezone.now()
        end_date_cache = None
        transaction.save()

    def test_normal_flow(self):
        gc = graphs_cache.Command()
        gc.save_cfd_data(self.board)
        cfd_list = models.ChartCFDData.objects.filter(day__gte=self.first_transaction.date.date())
        self.assertEqual(len(cfd_list), 5)
        
        cfd = cfd_list[0]
        data = json.loads(cfd.data)
        expected_todo_data = ['%s' % str(self.first_transaction.date.date()), 0, 0, 1]
        self.assertEqual(data, expected_todo_data)

        cfd = cfd_list[1]
        data = json.loads(cfd.data)
        expected_todo_data[0] = '%s' % str(self.first_transaction.date.date()+datetime.timedelta(days=1))
        self.assertEqual(data, expected_todo_data)

        cfd = cfd_list[2]
        data = json.loads(cfd.data)
        expected_doing_data = ['%s'
                % str(self.first_transaction.date.date()+datetime.timedelta(days=2)),
                0, 1, 0]
        self.assertEqual(data, expected_doing_data)

        cfd = cfd_list[3]
        data = json.loads(cfd.data)
        expected_doing_data[0] = '%s' % str(self.first_transaction.date.date()+datetime.timedelta(days=3))
        self.assertEqual(data, expected_doing_data)

        cfd = cfd_list[4]
        data = json.loads(cfd.data)
        expected_done_data = ['%s'
                % str(self.first_transaction.date.date()+datetime.timedelta(days=4)),
                1, 0, 0]
        self.assertEqual(data, expected_done_data)

    def test_columns_w_same_name(self):
        gc = graphs_cache.Command()

        card2 = models.Card()
        card2.board = self.board
        card2.card_id="1213"
        card2.end_date_cache=None
        card2.name="card 2"
        card2.save()

        column = models.Column()
        column.board = self.board
        column.board_position=3
        column.column_id="3"
        column.importance_order=3
        column.leadtime_period='None'
        column.name='Doinig'
        column.save()

        transaction = models.Transaction()
        transaction.card = card2
        transaction.column = column
        transaction.date = timezone.now()-datetime.timedelta(days=2)
        transaction.save()


        gc.save_cfd_data(self.board)

        today = datetime.date.today()
        cfd = models.ChartCFDData.objects.get(day=today)
        expected_done_data = ["%s" % today, 1, 1, 0]
        self.assertEqual(json.loads(cfd.data), expected_done_data)
