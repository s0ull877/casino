from django.urls import path

from .views import tictactoes_view, tictactoes_search, tictactoes_game_view

app_name = 'tictactoes'

urlpatterns = [
    path('', tictactoes_view, name='index'),
    path('search/', tictactoes_search, name='search'),
    path('game/<str:group_name>/', tictactoes_game_view, name='game'),
]
