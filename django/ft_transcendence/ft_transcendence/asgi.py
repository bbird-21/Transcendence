"""
ASGI config for ft_transcendence project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ft_transcendence.settings")


django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns as chat_urlpatterns
from game.routing import websocket_urlpatterns as game_urlpatterns

websocket_urlpatterns = chat_urlpatterns + game_urlpatterns
# Specify different handlers for different protocols, such as HTTP and WebSocket.
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,  # creates the ASGI application for handling HTTP requests.
        "websocket": AllowedHostsOriginValidator(  # WebSocket requests are routed through a series of middleware components
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
