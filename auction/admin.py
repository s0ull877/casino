from django.contrib import admin

from .models import Auction, AuctionBet

admin.site.register(Auction)
admin.site.register(AuctionBet)