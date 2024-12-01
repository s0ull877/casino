from django.urls import path

from .views import auctions_view, auction_view, auction_over_view, auction_create_view, diamond_auction_view

app_name = 'auction'

urlpatterns = [
    path('', auctions_view, name='index'),
    path('create/', auction_create_view, name='create'),
    path('diamond/', diamond_auction_view, name='diamond'),
    path('<str:group_name>/', auction_view, name='auction'),
    path('over/<str:group_name>/', auction_over_view, name='over'),
]