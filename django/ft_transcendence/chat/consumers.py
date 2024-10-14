import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import Chat
from chat.models import Message

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            chat = Chat.objects.get(id=self.room_name)
            self.room_group_name = 'chat_%s' % str(chat.id)
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()
        except Chat.DoesNotExist as e:
            print(e)
            return
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data_json = json.loads(text_data)
        print("===Received")
        print(data_json)

        message = data_json['message']
        # save message to database
        self.new_message(data_json)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def new_message(self, data):
        message = Message()
        message.refChat_id = data["refChat"]
        message.message = data["message"]
        message.author_id = data["author"]
        message.isRead = False
        message.type = data["type"]
        message.extraData = data["extraData"]
        message.save()

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))
