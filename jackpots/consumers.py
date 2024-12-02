
from datetime import timedelta
import json
from decimal import Decimal
from django.db.models import Count

from django.forms import ValidationError
from django.template.loader import render_to_string

from asgiref.sync import sync_to_async, async_to_sync

from channels.generic.websocket import WebsocketConsumer
from django.utils.timezone import now
from django.core.cache import cache






class AuctionConsumer(WebsocketConsumer):

    def connect(self):

        self.user = self.scope['user']
        self.group_name = self.scope['url_route']['kwargs']['group_name']

        ...




    def disconnect(self, code):

        ...

    def receive(self, text_data=None, bytes_data=None):

        ...