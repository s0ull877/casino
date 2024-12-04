import datetime
from django.shortcuts import render
from django.utils.timezone import now

from .models import Jackpots, JackpotBet

from .tasks import update_jackpot

def jackpot_view(request): 

    jackpot = Jackpots.objects.filter(active=True)
    if jackpot.exists():
        jackpot = jackpot.first()
    else:
        jackpot = Jackpots.objects.create(
            end_time = now() + datetime.timedelta(hours=23, minutes=58)
        )
        update_jackpot.apply_async(kwargs={'pk':jackpot.id}, eta=jackpot.end_time)

    bets = JackpotBet.objects.filter(jackpot=jackpot, deposit__gt=0).order_by('-deposit')
    print(jackpot.moscow_endtime)

    if not jackpot.winner:

        refresh_time = ((jackpot.end_time - now()).seconds + 3) * 1000 

        return render(request=request, template_name='jackpots/jackpot_game.html', context={'jackpot': jackpot, 'bets': bets, 'refresh_time': refresh_time})
    
    else:

        refresh_time = 61 * 1000

        winner_bet = jackpot.bets.get(user=jackpot.winner)

        return render(request=request, template_name='jackpots/jackpot_over.html', context={'jackpot': jackpot, 'bets': bets, 'refresh_time': refresh_time, 'winner_bet': winner_bet})
