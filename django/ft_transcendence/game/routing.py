from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/game/(?P<game_name>[-a-zA-Z0-9_]+)/', consumers.GameConsumer.as_asgi()),
    path('ws/waiting_game/<int:waitingGameID>/', consumers.WaitingConsumer.as_asgi())
]
