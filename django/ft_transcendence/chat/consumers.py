import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import Chat
from chat.models import Message
from django.contrib.auth.models import User

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        messages = Message.all_messages(self.room_name)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        author = data['from']
        author_user = User.objects.filter(username=author)[0]
        chat = Chat.objects.all()[0]
        message = Message.objects.create(
            author=author_user,
            message=data['message'],
            refChat=chat
        )
        print(f"data from {data['from']}")
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message),
            'from': data['from']
        }

        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []

        for message in messages:
            result.append(self.message_to_json(message))

        print(f"result : {result}")
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.message,
            'timestamp': str(message.createdAt)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        try:
            user = self.scope['user']
            print("=== user %s" % user)
            if str(user)=="AnonymousUser":
                print("==Not authorized")
                return
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
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
