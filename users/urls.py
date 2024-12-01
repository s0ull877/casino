from django.urls import path

from .views import login_view, games_view
app_name = 'auction'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('games/', games_view, name='games'),
]