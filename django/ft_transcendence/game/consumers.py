from channels.generic.websocket import WebsocketConsumer
from game.models import Game, Invitation
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
            waiting_game = Invitation.objects.get(id=self.waiting_game_id)
            self.player_one = waiting_game.invitation_sender
            self.player_two = waiting_game.invitation_receiver
        except Invitation.DoesNotExist as e:
            print(e)
            self.close()

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        if ( self.player_one == self.user ):
            waiting_game.player_one_conneted = True
            waiting_game.save()
        elif ( self.player_two == self.user ):
            waiting_game.player_two_conneted = True
            waiting_game.save()
        else:
            print("User unauthorized to connect to this session.")
            self.close()
        if ( waiting_game.player_one_conneted and waiting_game.player_two_conneted ):
            print("All Players Are Ready !")
        else:
            print("Waiting for Players")
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
