from django.urls import path

from .consumers import JackpotConsumer

ws_urlpatterns = [
    path('ws/jackpot/<str:group_name>/', JackpotConsumer.as_asgi()),
]