from django.urls import path

from .consumers import GameConsumer, GamesConsumer

ws_urlpatterns = [
    path('ws/games/', GamesConsumer.as_asgi()),
    path('ws/game/<str:group_name>/', GameConsumer.as_asgi()),
]

