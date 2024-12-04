from channels.generic.websocket import WebsocketConsumer
from game.models import Invitation
from asgiref.sync import async_to_sync
import json

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
        self.user = self.scope['user']
        self.waiting_game_id = self.scope["url_route"]["kwargs"]["waitingGameID"]
        self.room_group_name = f"game_{self.waiting_game_id}"

        try:
            self.waiting_game = Invitation.objects.get(id=self.waiting_game_id)
            self.player_one = self.waiting_game.invitation_sender
            self.player_two = self.waiting_game.invitation_receiver
        except Invitation.DoesNotExist as e:
            print(f"Invitation not found: {e}")
            self.close()

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        if self.player_one == self.user:
            self.waiting_game.player_one_connected = True
        elif self.player_two == self.user:
            self.waiting_game.player_two_connected = True
        else:
            print("Unauthorized user attempting to connect.")
            self.close()

        self.waiting_game.save()
        self.accept()

        # Notify the room about the connection status
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "update_status",
                "player_one_connected": self.waiting_game.player_one_connected,
                "player_two_connected": self.waiting_game.player_two_connected,
            },
        )

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)

        # Handle readiness
        if data["type"] == "ready":
            if self.user == self.player_one:
                self.waiting_game.player_one_ready = True
            elif self.user == self.player_two:
                self.waiting_game.player_two_ready = True
            self.waiting_game.save()

            # Notify all players about readiness updates
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "update_status",
                    "player_one_ready": self.waiting_game.player_one_ready,
                    "player_two_ready": self.waiting_game.player_two_ready,
                },
            )

            # Start countdown if both players are ready
            if self.waiting_game.player_one_ready and self.waiting_game.player_two_ready:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {"type": "start_countdown"},
                )

    def update_status(self, event):
        # Send status update to WebSocket
        self.send(text_data=json.dumps(event))

    def start_countdown(self, event):
        # Send countdown trigger to WebSocket
        self.send(text_data=json.dumps({"type": "start_countdown"}))
