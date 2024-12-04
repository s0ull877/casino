import random
from django.db import models
import pytz
from users.models import User
from shortuuid.main import ShortUUID
from django.core.validators import MinValueValidator

shortuuid = ShortUUID()

class Jackpots(models.Model):

    group_name = models.CharField(
        verbose_name='Имя для группы ws',
        max_length=64,
        default=shortuuid.uuid,
        editable=False, blank=True,
        unique=True
    )
    end_time = models.DateTimeField(
        verbose_name='Дата окончания аукциона'
    )
    active =models.BooleanField(
        verbose_name='Активен ли джекпот',
        default=True, blank=True
    )
    winner = models.ForeignKey(
        to=User, verbose_name='Победитель',
        on_delete=models.CASCADE,
        null=True, blank=True, default=None
    )

    @property
    def common_bank(self):

        common_bank = self.bets.aggregate(models.Sum('deposit'))['deposit__sum']
        return 0 if common_bank is None else common_bank 
    
    @property
    def moscow_endtime(self):

        return self.end_time.astimezone(pytz.timezone('Europe/Moscow'))
    
    def set_winner(self):

        bets = self.bets.order_by('-deposit')
        weights = []
        total = self.common_bank

        for bet in bets:

            weights.append(float(bet.deposit / total * 100) * 0.01)

        self.winner = random.choices(population=bets, weights=weights)[0].user

        self.save()


class JackpotBet(models.Model):

    jackpot = models.ForeignKey(
        to=Jackpots,
        on_delete=models.CASCADE,
        related_name='bets'
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='jackpot_bets'
    )
    deposit = models.DecimalField(
        verbose_name='Сумма ставки',        
        decimal_places=2,
        max_digits=13,
        validators=[MinValueValidator(1)],
        default=0
    )