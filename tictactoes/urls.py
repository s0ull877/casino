from django.urls import path

from .views import tictactoes_view, tictactoes_game_view

app_name = 'tictactoes'

urlpatterns = [
    path('', tictactoes_view, name='index'),
    path('game/<str:group_name>/', tictactoes_game_view, name='game'),
]
