from django.urls import path

from .consumers import GameConsumer

ws_urlpatterns = [
    path('ws/game/<str:group_name>/', GameConsumer.as_asgi()),
]

