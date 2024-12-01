import os

from django.core.asgi import get_asgi_application

from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from auction.routing import ws_urlpatterns as auction_routing
from tictactoes.routing import ws_urlpatterns as tictactoe_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

http_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': http_asgi_app,
    'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter([
        *auction_routing, *tictactoe_routing
    ]))),
})