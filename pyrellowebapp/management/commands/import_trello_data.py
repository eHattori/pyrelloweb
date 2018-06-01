from django.core.management.base import BaseCommand, CommandError
from pyrellowebapp import models

import json
import requests

class Command(BaseCommand):
    local_list_names = {}

    def get_all_board_columns(self, board_id, querystring):
        print("Saving columns...")
        querystring["cards"]="none"
        querystring["filter"]="all"
        url = "https://api.trello.com/1/boards/%s/lists" % board_id
        columns_response = requests.request("GET", url, params=querystring)
        columns_obj_list = []
        if columns_response.status_code == 200:
            columns_json = json.loads(columns_response.text)
            for column in columns_json:
                try:
                    column_obj = models.Column.objects.get(column_id=column["id"])
                except:
                    column_obj = models.Column()
                    column_obj.column_id = column["id"]

                column_obj.name = column["name"]
                column_obj.board_position = column["pos"]
                column_obj.active = not column["closed"]
                columns_obj_list.append(column_obj)
        return columns_obj_list



    def get_all_board_labels(self, board_id, querystring):
        print("Saving labels...")
        url = "https://api.trello.com/1/boards/%s/labels" % board_id
        labels_response = requests.request("GET", url, params=querystring)

        label_obj_list = []
        if labels_response.status_code == 200:
            labels_json = json.loads(labels_response.text)

            for label in labels_json:
                try:
                    label_obj = models.Label.objects.get(label_id=label["id"])
                except:
                    label_obj = models.Label()

                label_obj.label_id = label["id"]
                label_obj.name = label["name"]
                label_obj.color = label["color"]

                label_obj_list.append(label_obj)
        return label_obj_list


    def save_board_cards(self, card_dict, board):
        try:
            card_obj = models.Card.objects.get(card_id=card_dict["id"])
        except:
            card_obj = models.Card()

        card_obj.card_id=card_dict["id"]
        card_obj.name = card_dict["name"]
        labels=[]
        for label in card_dict["labels"]: 
            try:
                label_obj = models.Label.objects.get(label_id=label["id"])
                labels.append(label_obj)
            except Exception as e:
                pass
        try:
            card_obj.board = board
            card_obj.save()

            card_obj.labels.set(labels)

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

    def get_list_name(self, list_id):
        try:
            list_name = self.local_list_names[list_id]
        except:
            url = "https://api.trello.com/1/lists/%s" % list_id
            list_response = requests.request("GET", url)
            if list_response.status_code != 200:
                list_name = ""
            else:
                list_json = json.loads(list_response.text)
                list_name = list_json['name']

            self.local_list_names[list_id]=list_name
        return list_name


    def get_labels_column(self, labels_list):
        label_column = ""
        labels = []
        for label in labels_list:
            models.Label
            label_column += "%s," % label["name"]
        return label_column[:len(label_column)-1]


    def response_error(self, response):
        exit(response)


    def get_action_value(self, action):
        if action['type'] == "updateCard" and 'listAfter' in action['data']:
            list_key = "listAfter"
        elif action['type'] in ("createCard", "copyCard"):
            list_key = "list"
        else:
            return None
        try:

            action_dict = {
                'list_id': action['data'][list_key]['id'],
                'list_name': action['data'][list_key]['name'],
                'date': action['date']
            }
        except:
            action_dict = {
                'list_id': action['data'][list_key]['id'],
                'list_name': self.get_list_name(action['data'][list_key]['id']),
                'date': action['date']
            }
        return action_dict


    def get_leadtime_date(self, selected_columns, lists, card_dict):
        leadtime_date = ""
        for selected_column in selected_columns:
            list_id = ""
            for board_list in lists:
                if board_list["name"].upper() == selected_column.upper():
                    list_id = board_list["id"]
            if list_id in card_dict and card_dict[list_id] != "":
                leadtime_date = card_dict[list_id]
        return leadtime_date


    def get_card_list(self, board_id, querystring):
        card_params = "actions=copyCard,createCard,updateCard"
        card_url = "https://api.trello.com/1/boards/%s/cards?%s" % (
            board_id, card_params)

        card_response = requests.request("GET", card_url, params=querystring)

        if card_response.status_code != 200:
            self.response_error("%s - %s" % (card_response.status_code,
                card_response.text))

        data = json.loads(card_response.text)
        return data


    def handle(self, *args, **options):
        boards = models.Board.objects.all()

        for board in boards:

            querystring = {
                "key": board.trello_user_key,
                "token": board.trello_user_token
            }

            print("%s - exporting..." % board.name)
            board_id = board.board_id
            card_list = self.get_card_list(board_id, querystring)
            try: 
                board.label_set.set(self.get_all_board_labels(board.board_id,
                    querystring), bulk=False)
                board.column_set.set(self.get_all_board_columns(board.board_id,
                    querystring), bulk=False)
            except Exception as e:
                print(e)
                pass


            board_name = board.name

            try:
                start_columns = board.start_columns_str.split(",")
                end_columns = board.end_columns.split(",")
            except:
                start_columns = []
                end_columns = []


            columns = board.column_set


            for card in card_list:
                card_dict = {
                    'id': card["id"],
                    "name": card["name"],
                    "labels": card["labels"],
                    "start": "",
                    "end": "",
                    "transactions" : []
                }
                
                for action in card['actions']:
                    action_value = self.get_action_value(action)
                    if action_value != None:
                        try:
                            column = models.Column.objects.get(column_id = action_value["list_id"])

                            card_dict["transactions"].append( models.Transaction(
                                    date = action_value['date'], 
                                    column = column)
                            )

                        except Exception as e:
                            pass


                self.save_board_cards(card_dict, board)
            print("Board %s exported" % board_name)

        exit("Done")
