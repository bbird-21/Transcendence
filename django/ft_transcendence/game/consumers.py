from channels.generic.websocket import WebsocketConsumer  # type: ignore
import json
from asgiref.sync import async_to_sync
from game.models import Invitation


class WaitingConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.waiting_game_id = self.scope["url_route"]["kwargs"]["waitingGameID"]
        self.room_group_name = f"game_{self.waiting_game_id}"

        try:
            self.waiting_game = Invitation.objects.get(id=self.waiting_game_id)
            self.player_one = self.waiting_game.invitation_sender
            self.player_two = self.waiting_game.invitation_receiver
        except Invitation.DoesNotExist:
            self.close()
            return

        # Add user to the WebSocket group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

        # Send the current readiness state to the client
        self.send(text_data=json.dumps({
            "type": "current_state",
            "player_one_ready": self.waiting_game.player_one_ready,
            "player_two_ready": self.waiting_game.player_two_ready,
        }))

    def disconnect(self, close_code):
        try:
            waiting_game = Invitation.objects.get(id=self.waiting_game_id)

            if self.user == self.player_one:
                waiting_game.player_one_ready = False
                waiting_game.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "player_disconnected",
                        "player": "player_one",
                    },
                )
            elif self.user == self.player_two:
                waiting_game.player_two_ready = False
                waiting_game.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "player_disconnected",
                        "player": "player_two",
                    },
                )
        except Invitation.DoesNotExist:
            pass  # No action needed if the game no longer exists

        # Remove user from the WebSocket group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def player_disconnected(self, event):
        self.send(text_data=json.dumps({
            "type": "player_disconnected",
            "player": event["player"],
            "message": f"{event['player']} has disconnected.",
        }))

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
            else:
                return  # Ignore invalid actions

            waiting_game.save()

            # Broadcast readiness state
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "ready_state",
                    "player": player,
                    "ready": ready,
                },
            )

            # Check if both players are ready
            if waiting_game.player_one_ready and waiting_game.player_two_ready:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {"type": "start_countdown"},
                )

        except Invitation.DoesNotExist:
            self.close()

    def ready_state(self, event):
        self.send(text_data=json.dumps({
            "type": "ready_state",
            "player": event["player"],
            "ready": event["ready"],
        }))

    def start_countdown(self, event):
        self.send(text_data=json.dumps({"type": "start_countdown"}))
