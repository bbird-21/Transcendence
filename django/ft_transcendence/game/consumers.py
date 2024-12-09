from channels.generic.websocket import WebsocketConsumer # type: ignore
import json
from asgiref.sync import async_to_sync
from game.models import Invitation

class WaitingConsumer(WebsocketConsumer):
    def connect(self):
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

        # Accept the WebSocket connection
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        player = data.get("player")
        ready = data.get("ready")

        try:
            waiting_game = Invitation.objects.get(id=self.waiting_game_id)

            if player == "player_one" and self.user == self.player_one:
                waiting_game.player_one_ready = ready
            elif player == "player_two" and self.user == self.player_two:
                waiting_game.player_two_ready = ready

            waiting_game.save()

            # Broadcast the readiness state to all clients in the room
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "ready_state",
                    "player": player,
                    "ready": ready
                },
            )

            # If both players are ready, broadcast a countdown message
            if waiting_game.player_one_ready and waiting_game.player_two_ready:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {"type": "start_countdown"}
                )

        except Invitation.DoesNotExist:
            print("Invitation does not exist")
            self.close()

    def ready_state(self, event):
        # Send the readiness state to the WebSocket client
        self.send(text_data=json.dumps({
            "type": "ready_state",
            "player": event["player"],
            "ready": event["ready"]
        }))

    def start_countdown(self, event):
        # Start the countdown
        self.send(text_data=json.dumps({
            "type": "start_countdown"
        }))
