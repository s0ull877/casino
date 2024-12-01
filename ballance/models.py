from decimal import Decimal
from django.db import models
from django.dispatch import receiver
from django.forms import ValidationError

from users.models import User


class UserWallet(models.Model):

    user = models.OneToOneField(
        verbose_name='Владелец кошелька',
        to=User, on_delete=models.CASCADE,
        related_name='wallet'
    )
    ballance = models.DecimalField(
        verbose_name='Балланс кошелька',
        blank=True, default=0,
        decimal_places=2,
        max_digits=16,
    )

    def __str__(self):
        return f'{self.user.user_id} ballance:{self.ballance}$'
    
    def clean(self):
        if self.ballance < 0:
            raise ValidationError('Ballance cant be less 0')
        
    def transaction(self, sum, description):

        self.ballance += Decimal(sum)
        self.clean()
        self.save()
        BallanceTransaction.objects.create(
                ballance=self,
                sum=f'{sum}',
                description=description
            )

    

@receiver(models.signals.post_save, sender=User)
def create_wallet(sender, instance, using=None, **kwargs):
    if kwargs['created'] is True:
        UserWallet.objects.create(user=instance)


class BallanceTransaction(models.Model):

    ballance = models.ForeignKey(
        to=UserWallet, on_delete=models.CASCADE,
        related_name='transactions'
        )
    sum = models.DecimalField(
        verbose_name='Сумма транзакции',
        decimal_places=2,
        max_digits=13,
    )
    description= models.CharField(
        verbose_name='Описание',
        max_length=128
    )
    time = models.DateTimeField(
        verbose_name='Дата транзакции',
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.description} | {self.sum}$'



