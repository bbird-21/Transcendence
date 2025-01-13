import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import Chat
from chat.models import Message
from django.contrib.auth.models import User

class ChatConsumer(WebsocketConsumer):

    def mark_as_read(self, chat_id):
        chat = Chat.objects.get(id=chat_id)
        messages = chat.message_set.order_by('createdAt').filter(isRead=False)


        if messages:
            for message in messages:
                if message.author != self.user:
                    message.isRead = True
                    message.save()

    def fetch_messages(self, data):
        messages = Message.get_all_messages_from_chat(self.room_name)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        author_user = User.objects.get(username=data['author'])
        receiver    = User.objects.get(username=data['receiver'])
        chat = Chat.objects.get(id=self.room_name)
        message = Message.objects.create(
            author=author_user,
            message_receiver=receiver,
            message=data['message'],
            refChat=chat
        )

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }

        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []

        for message in messages:
            result.append(self.message_to_json(message))

        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.message,
            'refChat': str(message.refChat.id),
            'timestamp': str(message.createdAt)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        try:
            self.user = self.scope['user']
            print("=== user %s" % self.user)
            if str(self.user)=="AnonymousUser":
                print("==Not authorized")
                return
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            chat = Chat.objects.get(id=self.room_name)
            if chat.fromUser == self.user:
                self.user_id = chat.toUser
            else:
                self.user_id = chat.fromUser
            self.mark_as_read(chat.id)
            self.room_group_name = 'chat_%s' % str(chat.id)
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            print(f"{self.user} connected")
            self.accept()
        except Chat.DoesNotExist as e:
            print(e)
            return
    def disconnect(self, close_code):
        # Leave room group
        print(f"{self.user} disconnected")
        if ( self.room_group_name):
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
        author = message['message']['author']
        chat_id = message['message']['refChat']

        if self.user.username != author:
            self.mark_as_read(chat_id)
        self.send(text_data=json.dumps(message))
