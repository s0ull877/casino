from rest_framework import serializers
from .models import User, UserWallet

class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ('user_id', 'password', 'nickname', 'image',)

