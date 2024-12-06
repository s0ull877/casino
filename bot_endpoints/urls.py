from django.urls import path

from .views import ballance_apiview, create_user_apiview, transaction_apiview

from django.views.decorators.csrf import csrf_exempt

app_name = 'bot_endpoints'

urlpatterns = [
    path('save-user/', csrf_exempt(create_user_apiview)),
    path('ballance/', csrf_exempt(ballance_apiview)),
    path('ballance/history/', csrf_exempt(transaction_apiview))
]