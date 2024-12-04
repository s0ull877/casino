from time import sleep
from celery import shared_task

from .models import Jackpots
from ballance.models import UserWallet

@shared_task
def update_jackpot(pk):

    print(pk)
    jackpot = Jackpots.objects.get(pk=pk)
    try:
        jackpot.set_winner()
        wallet:UserWallet = UserWallet.objects.get(user=jackpot.winner)
        wallet.transaction(sum=jackpot.common_bank,
                           title="🏆 Джекпот", 
                           description=f"Победа #{jackpot.id}")
    except Exception as ex:
        print(ex)
    else:
        print('sleep')
        sleep(60)
    finally:
        jackpot.active = False
        jackpot.save()