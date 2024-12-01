from django.urls import path

from .views import ballance_apiview, create_user_apiview, transaction_apiview

app_name = 'bot_endpoints'

urlpatterns = [
    path('save-user/', create_user_apiview),
    path('ballance/', ballance_apiview),
    path('ballance/history/', transaction_apiview)
]