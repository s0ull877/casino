import json
from django.db import models

from users.models import User

from shortuuid.main import ShortUUID

shortuuid = ShortUUID()


class TicTacToe(models.Model):

    CHOICES=(
        ('3', '3',),
        ('5', '5',),
        ('8', '8',),
    )

    group_name = models.CharField(
        verbose_name='Имя для группы ws',
        max_length=64,
        default=shortuuid.uuid,
        editable=False, blank=True,
        unique=True
    )

    format = models.CharField(
        verbose_name='Формат карты',
        max_length=1,
        choices=CHOICES, 
        blank=False, null=False
    )

    first_player = models.ForeignKey(
        verbose_name='Игрок `X`',
        to=User, on_delete=models.CASCADE,
        related_name='tictactoe_firstplayer'
    )

    second_player = models.ForeignKey(
        verbose_name='Игрок `O`',
        to=User, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='tictactoe_secondplayer'
    )

    winner = models.ForeignKey(
        verbose_name='Победитель',
        to=User, on_delete=models.CASCADE,
        null=True, default=None, blank=True,
        related_name='tictactoe_winner'
    )

    bet = models.PositiveSmallIntegerField(
        verbose_name='Ставка',
        default=5
    )

    start_time = models.DateTimeField(
        verbose_name='Начало игры',
        auto_now_add=True
    )

    map = models.JSONField(
        verbose_name='Игровое поле'
    )

    

    @property
    def clean_map(self):
        return json.loads(self.map)['map']
    
    @clean_map.setter
    def clean_map(self, map):

        self.map = json.dumps({'map': map})

    
    def map_is_full(self):

        map = self.clean_map
        for row in map:

            if 0 in row:
                return False
            
        return True
    

    def get_winner(self, map):
            
        def func():

            f_diagonal = []
            s_diagonal = []
            for i in range(0, len(map)):

                f_diagonal.append(map[i][i])
                s_diagonal.append(map[i][len(map)-1-i])

                row_set = list(set(map[i]))
                if len(row_set) == 1 and row_set[0] != 0:
                    return row_set[0]

                column = []
                for j in range(0, len(map)):

                    column.append(map[j][i])

                column_set = list(set(column))
                if len(column_set) == 1 and column_set[0] != 0:
                    return column_set[0]

            f_diagonal = list(set(f_diagonal))
            if len(f_diagonal) == 1 and f_diagonal[0] != 0:
                return f_diagonal[0]
            
            s_diagonal = list(set(s_diagonal))
            if len(s_diagonal) == 1 and s_diagonal[0] != 0:
                return s_diagonal[0]
            
            return 0
        
        digit = func()
        if digit == 0:
            return None
        
        self.winner = self.first_player if digit == 1 else self.second_player
        self.save()
        return self.winner
            
        


    @classmethod
    def create_map(cls, digit):

        map = []
        for row in range(0, digit):
            map.append([])

            for column in range(0, digit):
                map[row].append(0)

        return json.dumps({'map': map})
    


