from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import integer_validator


class CustomUserManager(models.Manager):

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    def create_user(self, user_id, nickname, password=None, is_superuser=False, **kwargs):

        user = self.model(
            user_id=user_id,
            nickname=nickname,
            is_superuser=is_superuser, 
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, nickname, password, is_superuser=True, **kwargs):
        user = self.create_user(
            user_id=user_id,
            nickname=nickname,
            password=password,
            is_superuser=is_superuser,
            **kwargs
        )
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    user_id = models.CharField(
        unique=True,
        error_messages={
            'unique': _("A user with that user_id already exists."),
        },
        validators=[integer_validator],
        max_length=15,
    )
    nickname = models.CharField(
        verbose_name='Никнейм пользователя',
        max_length=32,
        blank=True, null=True
    )
    image = models.ImageField(
        verbose_name='аватар пользователя',
        upload_to='users_images',
        blank=True, default='users_images/avatar.jpg'
    )
    register_time = models.DateTimeField(
        verbose_name='Дата регистрации',
        auto_now_add=True, blank=True
    )

    is_superuser = models.BooleanField(
        _("admin status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )


    @property
    def is_staff(self):
        return self.is_superuser
    
    @property
    def total_bet(self):
        try:
            return self.wallet.transactions.filter(sum__lt=0).exclude(title__startswith="@").aggregate(models.Sum('sum'))['sum__sum'] * -1
        except TypeError:
            return 0
        
    def get_full_name(self):
        return ('%s %s') % (self.user_id, self.nickname)

    def get_short_name(self):
        return self.user_id
    


    USERNAME_FIELD = 'user_id'
    objects = CustomUserManager()
    REQUIRED_FIELDS = ['nickname']

