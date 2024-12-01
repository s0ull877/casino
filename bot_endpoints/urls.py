from django.urls import path

from .views import create_user

app_name = 'bot_endpoints'

urlpatterns = [
    path('save-user/', create_user),
]