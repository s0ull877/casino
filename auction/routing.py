from django.urls import path

from .consumers import AuctionsConsumer, AuctionConsumer

ws_urlpatterns = [
    path('ws/auctions/', AuctionsConsumer.as_asgi()),
    path('ws/auctions/<str:group_name>/', AuctionConsumer.as_asgi()),
]