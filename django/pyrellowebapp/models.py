from django.db import models


class Board(models.Model):
    name = models.CharField(max_length=250)
    board_id = models.CharField(max_length=250)
    start_columns_str = models.CharField(max_length=250, blank=True, null = True)
    end_columns_str = models.CharField(max_length=250, blank=True, null = True)
    trello_user_key = models.CharField(max_length=250)
    trello_user_token = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=250)
    label_id = models.CharField(max_length=250, unique=True)
    color = models.CharField(max_length=200, null=True, blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

LEADTIME_CHOICES = (
        ("Start", "Pode representar o início do Leadtime"),
        ("End", "Pode representar o fim do Leadtime"),
        ("None", "Não considerar nem como início nem fim")
)

class Column(models.Model):
    name = models.CharField(max_length=250)
    column_id = models.CharField(max_length=250, unique=True)
    active = models.BooleanField(default=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE) 
    importance_order = models.IntegerField(default=1000)
    leadtime_period = models.CharField(
            max_length=5,
            choices = LEADTIME_CHOICES,
            default = "None",
        )

    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]


class Card(models.Model):
    card_id = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    choice_text = models.CharField(max_length=200)
    labels = models.ManyToManyField(Label)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)


class Transaction(models.Model):
    date = models.DateTimeField()
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('column', 'date',)
