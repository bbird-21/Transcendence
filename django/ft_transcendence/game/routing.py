from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<game_name>[-a-zA-Z0-9_]+)/', consumers.GameConsumer.as_asgi()),
]
