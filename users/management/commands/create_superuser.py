
from typing import Any
from users.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    
    _class=User
    name='SUPERUSER'

    def handle(self, *args: Any, **options: Any) -> str | None:
        self._class.objects.create_superuser(user_id='80082', nickname='admin', password='123486215382')
