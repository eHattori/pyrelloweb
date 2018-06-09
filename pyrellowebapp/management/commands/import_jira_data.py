from django.core.management.base import BaseCommand, CommandError
from pyrellowebapp import models

import json
import requests

class Command(BaseCommand):
    local_list_names = {}

    def add_arguments(self, parser):
        parser.add_argument(
        '--board',
            action='store',
            dest='board',
            type=str,
            default="",
            help='Import the board with this id',
        )


    def save_board_cards(self, card_dict, board):
        try:
            card_obj = models.Card.objects.get(card_id=card_dict["card_id"])
        except:
            card_obj = models.Card()

        card_obj.card_id=card_dict["card_id"]
        card_obj.name = card_dict["name"]
        try:
            card_obj.board = board
            card_obj.save()
            card_obj.labels.set(card_dict["labels"])

            card_obj.save()
        except Exception as e:
            print(e)
            pass
        for transaction in card_dict["transactions"]:
            try:
                transaction.card = card_obj
                transaction.save()
            except Exception as e:
                pass



    def response_error(self, response):
        exit(response)



    def handle(self, *args, **options):
        from jira import JIRA
        if options['board'] != "":
            boards = models.Board.objects.filter(board_id=options['board'])
        else:
            boards = models.Board.objects.filter(board_type="jira")
        for board in boards:
            columns = {}
            settings ={
                    'options':{'server': board.jira_server_url},
                    'JIRA_USER': board.trello_user_key,
                    'JIRA_PASSWORD': board.trello_user_token,
                    'BOARD_NAME': board.board_id
            }

            jira = JIRA(options=settings['options'], basic_auth= (settings['JIRA_USER'], settings['JIRA_PASSWORD']))
            issues = jira.search_issues('project='+ settings['BOARD_NAME'], startAt=0,
                    maxResults=200, json_result=True)

            issues = issues['issues']
            issues = {issue['key']:issue for issue in issues}
            for key, issue in issues.items():  

                issue = jira.issue(key, expand='changelog')
                try:
                    label_obj = models.Label.objects.get(label_id=issue.fields.issuetype.name)
                except:
                    label_obj = models.Label()
                label_obj.name = issue.fields.issuetype.name
                label_obj.label_id = issue.fields.issuetype.name
                label_obj.board = board
                label_obj.save()

                labels = [label_obj]

                
                for label in issue.fields.labels:
                    try:
                        label_obj = models.Label.objects.get(label_id=label)
                    except:
                        label_obj = models.Label()
                    label_obj.label_id = label
                    label_obj.name = label
                    label_obj.board = board
                    label_obj.save()
                    labels.append(label_obj)
                card_dict = {
                    'card_id': issue.id,
                    "name": issue.key,
                    "labels": labels,
                    "transactions" : [],
                    "columns": []
                }
 
                
                for history in issue.changelog.histories:
                    for item in history.items:
                        if item.field == 'status':
                            try:
                                column =  models.Column.objects.get(column_id = item.to)
                            except Exception as e:
                                print(e)
                                column = models.Column()
                        
                            column.column_id = item.to
                            column.name = item.toString
                            column.board_id = board.id
                            column.save()
                            card_dict['columns'].append(column)

                            card_dict["transactions"].append( models.Transaction(
                                    date = history.created, 
                                    column = column)
                            )
                board.column_set.set(card_dict['columns'])
                board.save()
                self.save_board_cards(card_dict, board)
            print("Board %s exported" % board.name)

        print("Done")
