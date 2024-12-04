
from datetime import timedelta
import json
from decimal import Decimal

from django.forms import ValidationError
from django.template.loader import render_to_string

from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer, StopConsumer
from django.utils.timezone import now
from django.core.cache import cache

from .models import JackpotBet, Jackpots

class JackpotConsumer(WebsocketConsumer):

    def connect(self):

        self.user = self.scope['user']
        self.group_name = 'jackpot_' + self.scope['url_route']['kwargs']['group_name']

        self.jackpot = Jackpots.objects.prefetch_related('bets').get(group_name=self.scope['url_route']['kwargs']['group_name'])
        self.bet = JackpotBet.objects.get_or_create(
            user=self.user,
            jackpot = self.jackpot
        )[0]

        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, code):

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        
        raise StopConsumer()


    def get_html(self):

        bets = ''
        bets_progressbar = ''
        bets_objects = JackpotBet.objects.select_related('user').filter(deposit__gt=0, jackpot=self.jackpot).order_by('-deposit')

        for bet in bets_objects:
            bets_progressbar += f'<div id="user-{bet.user.id}" class="box" data-value="{bet.deposit}"></div>'
        
            bets += render_to_string('jackpots/includes/user_div.html', context={
                'bet': bet
            })

        return bets, bets_progressbar, bets_objects.count()


    def receive(self, text_data=None, bytes_data=None):

        if text_data == 'over':
            self.close(code=1000, reason='auction is over')
            self.disconnect(1000)

        wallet = self.user.wallet
        current_ballance = str(wallet.ballance)

        try:
            wallet.transaction(Decimal(text_data) * -1, "🏆 Джекпот", f"Депозит #{self.jackpot.id}")
        
        except ValidationError:
            
            self.send(json.dumps({
                'event': 'incorrect_bet',
                'ballance': current_ballance,
            }))

        else:

            self.send(json.dumps({
                'event': 'correct_bet',
                'ballance': str(wallet.ballance),
            }))

            self.bet.deposit += Decimal(text_data)
            self.bet.save()

            event = {
                'type': 'update_deposits_handler'
            }

            async_to_sync(self.channel_layer.group_send)(
               self.group_name, event
            )

    def update_deposits_handler(self, event):

        bets, bets_bar, count = self.get_html()

        context = {
            'event': 'update_deposits',
            'html': bets,
            'bets_bar': bets_bar,
            'count': count,
            'common_bank': str(self.jackpot.common_bank)
        }

        self.send(json.dumps(context))
