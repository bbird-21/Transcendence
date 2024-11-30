from channels.generic.websocket import WebsocketConsumer
from game.models import Game
from asgiref.sync import async_to_sync
from django.db.models import Q

class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.game_name = self.scope["url_route"]["kwargs"]["game_name"]
        self.room_group_name = f"chat_{self.game_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

class WaitingConsumer(WebsocketConsumer):
    def connect(self):
        # print("Attempting to connect to game:", self.scope["url_route"]["kwargs"]["waitingGameID"])
        self.user = self.scope['user']
        self.waiting_game_id = self.scope["url_route"]["kwargs"]["waitingGameID"]
        self.room_group_name = f"game_{self.waiting_game_id}"
        try:
            # Check if the game exists
            game = Game.objects.filter(Q(player_one=self.user) | Q(player_two=self.user))[0]
        except Game.DoesNotExist as e:
            print(e)
            self.close()
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        if (game.player_one == self.user ):
            game.player_one_conneted = True
            game.save()
        else:
            game.player_two_conneted = True
            game.save()
        if ( game.player_one_conneted and game.player_two_conneted ):
            print("All Players Are Ready !")
        else:
            print("Waiting for Players")
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
