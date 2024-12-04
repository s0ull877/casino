from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

from .models import TicTacToe

from decimal import Decimal

@login_required
def tictactoes_view(request):
    
    if request.method == "POST":

        try:
            bet = Decimal(request.POST.get('bet'))
            format = request.POST.get('format')
            if request.user.wallet.ballance >= bet:

                game = TicTacToe.objects.create(
                    format = format,
                    first_player=request.user,
                    bet=bet, map=TicTacToe.create_map(int(format))
                )

                return render(request, f'tictactoes/base_game.html', context={'game': game})

        except Exception as ex:
            raise Http404()

    return render(request, 'tictactoes/tiktaktoe.html')
    
    
@login_required
def tictactoes_game_view(request, group_name):

    try:
        game = TicTacToe.objects.get(group_name=group_name)
    except TicTacToe.DoesNotExist:
        raise Http404()
    
    if game.winner:

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    
    if request.user is not game.first_player and game.second_player is None:
        game.second_player = request.user
        game.save()
    
    if game.second_player is not None and request.user not in game.players:
        raise Http404()
    
    return render(request=request, template_name='tictactoes/base_game.html', context={'game': game})

