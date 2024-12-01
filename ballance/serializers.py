from rest_framework import serializers
from .models import User, UserWallet, BallanceTransaction

class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ('user_id', 'password', 'nickname', 'image',)


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        
        model = BallanceTransaction
        fields = ('sum', 'description',)
