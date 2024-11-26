from channels.generic.websocket import WebsocketConsumer

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
