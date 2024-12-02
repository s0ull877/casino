from rest_framework import serializers
from .models import User, UserWallet, BallanceTransaction

class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ('user_id', 'password', 'nickname', 'image',)

    def create(self, validated_data):

        instance = User.objects.create_user(**validated_data)
        return instance

class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        
        model = BallanceTransaction
        fields = ('sum', 'title', 'description', 'time',)
