from rest_framework import serializers
from .models import UserWallet, BallanceTransaction, User

class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ('user_id', 'password', 'nickname', 'image',)

