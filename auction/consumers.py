
from datetime import timedelta
import json
from decimal import Decimal
from django.db.models import Count

from django.forms import ValidationError
from django.template.loader import render_to_string

from asgiref.sync import sync_to_async, async_to_sync

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, StopConsumer
from django.utils.timezone import now
from django.core.cache import cache

from .models import Auction, AuctionBet
from ballance.models import BallanceTransaction


class AuctionsConsumer(AsyncWebsocketConsumer):

    ordering = [1,10]

    async def connect(self):
        
        await self.accept()

        await self.send_auctions()


    async def send_auctions(self):
        
        auctions, diamond_members = await self.get_data()
        html = ''
        async for auction in auctions:
            
            html += render_to_string(template_name='auctions/includes/auction_div.html', 
                                    context={
                                        'auction': auction.display_json()
                                        })
        
        await self.send(text_data=json.dumps({
            'html': html,
            'diamond_members': diamond_members
        }))


    @sync_to_async
    def get_data(self):
        try:
            auctions= Auction.objects.select_related('owner').prefetch_related('members').\
                annotate(members_count=Count('members__id', distinct=True)).\
                    filter(active=True, min_bet__range=self.ordering).exclude(owner=None).order_by('-members_count')
        except Auction.DoesNotExist:
            auctions = None

        diamond_members = Auction.objects.prefetch_related('members').filter(owner=None, active=True).first().members.count()
        
        return auctions, diamond_members
        

    async def receive(self, text_data=None, bytes_data=None):

        if text_data:
            self.ordering = list(map(int, text_data.split('-')))

        await self.send_auctions()



class AuctionConsumer(WebsocketConsumer):

    def connect(self):

        self.user = self.scope['user']
        self.group_name = self.scope['url_route']['kwargs']['group_name']

        self.auction = Auction.objects.select_related('owner').prefetch_related('members').get(group_name=self.group_name)
        self.leader = self.auction.leader
        self.bet = AuctionBet.objects.get_or_create(
            owner=self.user,
            auction = self.auction
        )[0]

        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        members = self.auction.members.all()
        self.members_count = members.count()

        if self.members_count < self.auction.max_members:

            self.auction.members.add(self.user.id)
            self.auction.save()
            self.online_time = now()

            self.update_members()
            
            self.accept()

            time_data = cache.get(self.group_name) # (сколько на таймере в layer, сколько всего)

            try:
                last_time = now() - time_data[0]
                if int(last_time.total_seconds()) > time_data[1]:
                    self.close(code=1000, reason='auction is over')
                    self.disconnect(1000)
                self.send(json.dumps({
                    'event': 'connect',
                    'time': time_data[1] - int(last_time.total_seconds()),
                    'total': time_data[1]
                }))
            except TypeError:
                self.close(code=3000, reason='server error')
                self.disconnect(3000)

        else:

            self.close(code=3000, reason='room is full')
            self.disconnect(3000)




    def disconnect(self, code):

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        
        self.auction.members.remove(self.user)
        self.auction.save()

        self.update_members()

        raise StopConsumer()


    def update_members(self):

        members_count = self.auction.members.count() 

        if members_count == 0:

            self.auction.active = False
            self.auction.save(update_fields=['active'])

        if members_count == 1 and members_count > self.members_count:

            cache.set(self.auction.group_name, (now(), 60))


        event = {
            'type': 'members_handler',
            'members_count': members_count,
        }

        async_to_sync(self.channel_layer.group_send)(
            self.group_name, event
        )
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {'type': 'update_deposits_handler'}
        )


    def members_handler(self, event):

        self.send(json.dumps({
            'event': 'members_handler',
            'span_id': f'auction-members-{self.auction.id}',
            'count': event['members_count'],
        }))


    def get_html(self):

        bets = ''
        bets_objects = AuctionBet.objects.select_related('owner').filter(deposit__gt=0, auction=self.auction).order_by('-deposit')

        if not bets_objects.filter(owner=self.user).exists() and now() - self.online_time >= timedelta(minutes=1):
            self.close(code=3000, reason='user is not active')
            self.disconnect(3000)

        for bet in bets_objects:
        
            bets += render_to_string('auctions/includes/user_div.html', context={
                'member': bet.owner,
                'bet': bet
            })

        leader = render_to_string('auctions/includes/auction_leader.html', context={
                'auction': self.auction,
        })

        return bets, leader


    def receive(self, text_data=None, bytes_data=None):

        if text_data == 'over':
            self.close(code=1000, reason='auction is over')
            self.disconnect(1000)

        wallet = self.user.wallet
        current_ballance = str(wallet.ballance)

        try:
            wallet.transaction(Decimal(text_data) * -1, "💎 Аукцион", f"Депозит #{self.auction.id}")
        
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

        bets, leader = self.get_html()

        context = {
            'event': 'update_deposits',
            'html': bets,
            'leader': leader,
            'update_timer': '',
            'time': 15,
            'total': 15
        }

        current_leader = self.auction.leader

        if self.leader != current_leader and current_leader.deposit != Decimal(0):
            cache.set(self.auction.group_name, value=(now(), 15))
            context['update_timer'] = 'true'
            self.leader = current_leader


        self.send(json.dumps(context))
