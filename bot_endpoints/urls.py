from django.urls import path

from .views import ballance_view, create_user

app_name = 'bot_endpoints'

urlpatterns = [
    path('save-user/', create_user),
    path('ballance/', ballance_view)
]