import json
from rest_framework import response, status
from rest_framework.decorators import api_view

from django.core.exceptions import BadRequest
from ballance.serializers import UserSerializer, UserWallet, BallanceTransaction


@api_view(['POST'])
def create_user(request):

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save()
        return response.Response(status=status.HTTP_201_CREATED)
    
    else:

        return response.Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def get_ballance_view(request):

    