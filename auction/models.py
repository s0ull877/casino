from django.db import models
from django.dispatch import receiver

from django.core.validators import MinValueValidator

from users.models import User
from ballance.models import UserWallet

from shortuuid.main import ShortUUID

shortuuid = ShortUUID()

class Auction(models.Model):

    group_name = models.CharField(
        verbose_name='Имя для группы ws',
        max_length=64,
        default=shortuuid.uuid,
        editable=False, blank=True,
        unique=True
    )
    owner = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='auctions_owner',
        blank=True, null=True
    )

    start_time = models.DateTimeField(
        verbose_name='Дата создания аукциона',
        auto_now_add=True,
    )

    active =models.BooleanField(
        verbose_name='Активен ли аукцион',
        default=True
        )
    max_members = models.PositiveSmallIntegerField(
        verbose_name='Кол-во игроков',
        default=20
    )
    members = models.ManyToManyField(
        to=User, related_name='auctions_member',
        blank=True
    )

    min_bet = models.PositiveIntegerField(
        verbose_name='Минимальная ставка',
        default=1
    )

    def __str__(self):
        return f'{self.owner.user_id} {self.start_time}' if self.owner else f'DIAMOND {self.start_time}'
    
    @property
    def common_bank(self):

        common_bank = self.bets.aggregate(models.Sum('deposit'))['deposit__sum']
        return 0 if common_bank is None else common_bank


    @property 
    def leader(self):

        try:
            return self.bets.select_related('owner').filter(deposit__gt=0).order_by('-deposit').first()
        except Exception:
            return 0

    def display_json(self):

        return {
            'id': self.pk,
            'group_name': self.group_name,
            'owner': self.owner.nickname,
            'min_bet': self.min_bet,
            'max_members': self.max_members,
            'members_count': self.members.count()
        }
    
@receiver(models.signals.post_save, sender=Auction)
def post_save(sender, instance, using=None, **kwargs):
    try:
        if next(iter(kwargs['update_fields'])) == 'active':

            leader = instance.leader
            
            if not leader:
                instance.delete()
            else:
                wallet = UserWallet.objects.get(user=leader.owner)
                wallet.transaction(instance.common_bank, f"Auction win #{instance.pk}")

    except TypeError:
        pass



class AuctionBet(models.Model):

    owner = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE
    )
    deposit = models.DecimalField(
        verbose_name='Сумма ставки',
        decimal_places=2,
        max_digits=13,
        validators=[MinValueValidator(1)],
        default=0
    )
    auction = models.ForeignKey(
        to=Auction,
        on_delete=models.CASCADE,
        related_name='bets'
    )

    def __str__(self):
        return f'{self.owner.user_id} {self.deposit}'