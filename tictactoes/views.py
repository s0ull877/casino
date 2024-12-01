from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import TicTacToe

def tictactoes_view(request):

    return render(request, 'tictactoes/index.html')

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

    
def tictactoes_search(request):

    if request.GET.get('map') not in ['3', '5', '8']:
        raise Http404()
    
    games = TicTacToe.objects.filter(second_player=None, format=request.GET.get('map'))

    if games.exists():
    
        game = games.first()
        if request.user != game.first_player:
            game.second_player = request.user
            game.save()
    
    else:
        map = TicTacToe().create_map(int(request.GET.get('map')))
        game = TicTacToe.objects.create(
            format=request.GET.get('map'),
            first_player=request.user,
            map=map
        )
    
    return HttpResponseRedirect(reverse('tictactoes:game', kwargs={'group_name':game.group_name}))
