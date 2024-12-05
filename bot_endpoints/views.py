from decimal import InvalidOperation
from django.forms import ValidationError
from rest_framework import response, status
from rest_framework.decorators import api_view

from ballance.models import UserWallet, BallanceTransaction
from ballance.serializers import UserSerializer, TransactionSerializer


@api_view(['POST'])
def create_user_apiview(request):

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save()
        return response.Response(status=status.HTTP_201_CREATED)
    
    else:

        return response.Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST', 'DELETE'])
def ballance_apiview(request):

    try:
        user_id = request.query_params['user_id']
        wallet: UserWallet = UserWallet.objects.prefetch_related('user').get(user__user_id=user_id)

    except KeyError:
        return response.Response(data={'error': 'Invalid query params, expected `user_id`'}, status=status.HTTP_400_BAD_REQUEST)
    except UserWallet.DoesNotExist:
        return response.Response(data={'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    try:

        if request.method == 'DELETE':

            wallet.user.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)


        if request.method == 'POST':
                
            try:

                wallet.transaction(**request.data)
        
            except TypeError as ex:
                return response.Response(data={'error': str(ex)[str(ex).find('got an'): -1]}, status=status.HTTP_400_BAD_REQUEST)
            
            except InvalidOperation:
                return response.Response(data={'error': 'Sum must be digits'}, status=status.HTTP_400_BAD_REQUEST)
            
            except ValidationError as ex:
                return response.Response(data={'error': ex.message}, status=status.HTTP_402_PAYMENT_REQUIRED)

        return response.Response(data={'user_id': user_id, 'ballance': wallet.ballance}, status=status.HTTP_200_OK)
                

    except Exception as ex:
        return response.Response(data={'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def transaction_apiview(request):

    try:
        user_id = request.data['user_id']
        wallet: UserWallet = UserWallet.objects.prefetch_related('user').get(user__user_id=user_id)

    except KeyError:
        return response.Response(data={'error': 'Invalid data, expected `user_id`'}, status=status.HTTP_400_BAD_REQUEST)
    except UserWallet.DoesNotExist:
        return response.Response(data={'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    
    queryset = BallanceTransaction.objects.filter(ballance=wallet)
    serializer = TransactionSerializer(queryset, many=True)

    return response.Response(data={'user_id': user_id, 'ballance': wallet.ballance, 'history': serializer.data}, status=status.HTTP_200_OK)    