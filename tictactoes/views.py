from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

from .models import TicTacToe

from decimal import Decimal

def tictactoes_view(request):
    
    if request.method == "POST":

        try:
            bet = Decimal(request.POST.get('bet'))
            format = request.POST.get('format')
            if request.user.wallet.ballance >= bet:

                game = TicTacToe.object.create(
                    format = format,
                    first_player=request.user,
                    bet=bet, map=TicTacToe.create_map(int(format))
                )

                return render(request, f'tictactoes/tiktaktoe_game{format}.html', context={'game': game})

        except:
            raise Http404()

    return render(request, 'tictactoes/tiktaktoe.html')
    
    

def tictactoes_game_view(request, group_name):

    try:
        game = TicTacToe.objects.get(group_name=group_name)
    except TicTacToe.DoesNotExist:
        raise Http404()
    
    if game.winner:

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    
    if request.user not in [game.first_player, game.second_player]:
        raise Http404()
    
    return render(request=request, template_name='tictactoes/game.html', context={'game': game})

