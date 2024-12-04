from django.urls import path

from .views import jackpot_view

app_name = 'jackpots'

urlpatterns = [
    path('', jackpot_view, name='index')
]