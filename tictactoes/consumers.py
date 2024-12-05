import os
from datetime import timedelta
import json
from decimal import Decimal

from django.forms import ValidationError
from django.template.loader import render_to_string

from asgiref.sync import async_to_sync, sync_to_async

from channels.generic.websocket import WebsocketConsumer, StopConsumer, AsyncWebsocketConsumer
from django.utils.timezone import now
from django.core.cache import cache

from .models import TicTacToe

class GamesConsumer(AsyncWebsocketConsumer):

    ordering = [1,10]

    async def connect(self):
        os.environ['online'] = str(int(os.getenv('online')) + 1)
        
        await self.accept()

        await self.send_games()

    async def disconnect(self, code):
        os.environ['online'] = str(int(os.getenv('online')) - 1)

        return await super().disconnect(code)


    async def send_games(self):
        
        games = await self.get_data()
        html = ''
        async for game in games:
            
            html += render_to_string(template_name='tictactoes/includes/game_div.html', 
                                    context={'game': game})
        
        await self.send(text_data=json.dumps({
            'html': html,
        }))


    @sync_to_async
    def get_data(self):
        try:
            games= TicTacToe.objects.select_related('first_player'). \
                filter(second_player=None, winner=None, bet__range=self.ordering).order_by('-start_time')
        except TicTacToe.DoesNotExist:
            games = None

        return games
        

    async def receive(self, text_data=None, bytes_data=None):

        if text_data:
            self.ordering = list(map(int, text_data.split('-')))

        await self.send_games()


class GameConsumer(WebsocketConsumer):

    def connect(self):
        os.environ['online'] = str(int(os.getenv('online')) + 1)

        self.user = self.scope['user']
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.game = TicTacToe.objects.get(group_name=self.group_name)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        # второй игрок появился
        if self.game.second_player is not None and not cache.get(f'game_{self.group_name}'):

            cache.set(f'game_{self.group_name}', now())
            try:
                self.game.first_player.wallet.transaction(self.game.bet * -1,'❌ Крестики-нолики', f'Участие #{self.game.id}')
                self.game.second_player.wallet.transaction(self.game.bet * -1, '❌ Крестики-нолики', f'Участие #{self.game.id}')
            except ValidationError:
                # some_code
                ...

            event = {
                'type': 'start_game_handler'
            }

            async_to_sync(self.channel_layer.group_send)(
                self.group_name, event
            )

        # если ктото переподключился
        elif self.game.second_player is not None: 

            map = self.game.clean_map
            event = {
                'type': 'update_map_handler',
                'map': map
            }

            self.update_map_handler(event)

        # инициализация игры первым игроком
        else:

            pass


    def start_game_handler(self, event):

        self.game = TicTacToe.objects.get(group_name=self.group_name)
        context ={
            'event': 'start',
            'move': 'first-player',
            'oponent':  self.game.second_player.nickname if self.user == self.game.first_player else self.game.first_player.nickname,
            'oponent_image':  self.game.second_player.image.url if self.user == self.game.first_player else self.game.first_player.image.url,
        }
        self.send(json.dumps(context))


    def receive(self, text_data: str=None, bytes_data=None):
        next_move, instance_digit, row, column = self.get_move_data(text_data)
        
        map = self.game.clean_map
        map[row][column] = instance_digit

        winner = self.game.get_winner(map)
        if winner:
            winner.wallet.transaction(self.game.bet * 2,'❌ Крестики-нолики', f'Победа #{self.game.id}')
            event = {
                'type': 'update_map_handler',
                'map': map,
                'winner': self.game.winner.nickname
            }

        else:
            event = {
                'type': 'update_map_handler',
                'map': map,
            }

        cache.set(f'game_{self.group_name}', now())
        cache.set(f'game_{self.group_name}_queue', next_move)

        async_to_sync(self.channel_layer.group_send)(
            self.group_name, event
        )


    def update_map_handler(self, event):

        self.game.clean_map = event['map']
        self.game.save()

        if event.get('winner'):
            self.send(json.dumps({
                'event': 'winner',
                'map': self.game.clean_map,
                'winner': event['winner']
            }))
            return

        if self.game.map_is_full():
            self.game.map = TicTacToe().create_map(int(self.game.format))
            self.game.save()

        last = now() - cache.get(f'game_{self.group_name}')

        self.send(json.dumps({
            'event': 'update_map',
            'map': self.game.clean_map,
            'move': cache.get(f'game_{self.group_name}_queue'),
            'seconds': int(60 - last.total_seconds()),
        }))


    def get_move_data(self, text_data: str) -> tuple[str, int, int, int]:

        list_data = text_data.split('/')
        instance_digit = 1 if list_data[0] == 'first-player' else 2
        next_move = 'second-player' if list_data[0] == 'first-player' else 'first-player'

        return next_move, instance_digit, int(list_data[-1][0]), int(list_data[-1][-1])


    def disconnect(self, code):
        os.environ['online'] = str(int(os.getenv('online')) - 1)

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        
        if not self.game.second_player:
            self.game.delete()

        raise StopConsumer()



    