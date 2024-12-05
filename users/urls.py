from django.urls import path

from .views import login_view, games_view, profile_view, top_users_view, settings_view, theme_view, lang_view
app_name = 'auction'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('games/', games_view, name='games'),
    path('profile/', profile_view, name='profile'),
    path('top/', top_users_view, name='top'),
    path('settings/', settings_view, name='settings'),
    path('theme/', theme_view, name='change_theme'),
    path('lang/', lang_view, name='change_lang'),
]