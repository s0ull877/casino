from django.contrib import admin

from .models import UserWallet, BallanceTransaction

admin.site.register(UserWallet)
admin.site.register(BallanceTransaction)
