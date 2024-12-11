from channels.generic.websocket import WebsocketConsumer  # type: ignore
import json
from asgiref.sync import async_to_sync
from game.models import Invitation
import random

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
            if self.user == self.player_one:
                self.waiting_game.player_one_ready = False
                self.waiting_game.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "player_disconnected",
                        "player": "player_one",
                    },
                )
            elif self.user == self.player_two:
                self.waiting_game.player_two_ready = False
                self.waiting_game.save()
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
        action = data.get("action")

        if action is not None:
            self.play()

        try:
            if player == "player_one" and self.user == self.player_one:
                print("player one ready")
                self.waiting_game.player_one_ready = True
            elif player == "player_two" and self.user == self.player_two:
                print("player two ready")
                self.waiting_game.player_two_ready = True
            self.waiting_game.save()


            # Check if both players are ready
            if self.waiting_game.player_one_ready == True and self.waiting_game.player_two_ready == True:
                print("start countdown")
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {"type": "start_countdown"},
                )

            # Broadcast readiness state
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "ready_state",
                    "player": player,
                    "ready": ready,
                },
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

    def play(self):
        # url = '/game/play/' + self.waiting_game.id
        # Send a message to the client to redirect them to the play page
        self.send(json.dumps({
            "type": "redirect",
            "url": "/game/play/" + str(self.waiting_game.id)  # Replace with the actual URL of your play page
        }))

class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['GameID']
        self.room_group_name = f"game_{self.game_id}"

        print(f"Connecting player to game {self.game_id}")

        # Ensure the game state is initialized
        if not hasattr(self.channel_layer, "game_state"):
            self.channel_layer.game_state = {}

        # Initialize the game state for the specific room if not set
        if self.room_group_name not in self.channel_layer.game_state:
            print(f"Initializing game state for {self.room_group_name}")
            self.channel_layer.game_state[self.room_group_name] = self.initialize_game_state()

        # Add the player to the group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        # Update the players_connected count
        game_state = self.channel_layer.game_state[self.room_group_name]
        game_state['players_connected'] += 1
        print(f"Players connected: {game_state['players_connected']}")

        # If both players are connected, start the game
        if game_state['players_connected'] == 2:
            self.start_game()

        # Send the current game state to the connected player
        self.send_game_state()

    def disconnect(self, close_code):
        # Decrement the number of connected players on disconnect
        game_state = self.channel_layer.game_state.get(self.room_group_name, {})
        if game_state:
            game_state['players_connected'] -= 1

        print(f"Player disconnected. Players connected: {game_state['players_connected']}")

        # Clean up the group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def start_game(self):
        """Start the game by setting initial ball and paddle positions."""
        game_state = self.channel_layer.game_state[self.room_group_name]
        
        # Reset game state values (positions, scores, etc.)
        game_state['ball'] = {'top': 50, 'left': 50}
        game_state['paddle1'] = {'top': 50}
        game_state['paddle2'] = {'top': 50}
        game_state['score1'] = 0
        game_state['score2'] = 0
        game_state['dx'] = 1 if random.choice([True, False]) else -1
        game_state['dy'] = 1 if random.choice([True, False]) else -1
        game_state['status'] = 'playing'  # Mark the game as 'playing'
        
        print("Game started!")

        # Broadcast the start game event to all connected players
        self.broadcast_game_state()

    def receive(self, text_data):
        """Handle incoming messages."""
        data = json.loads(text_data)
        game_state = self.channel_layer.game_state[self.room_group_name]

        if data['type'] == 'move_paddle':
            player = data['player']
            top = data['top']
            if player == 1:
                game_state['paddle1']['top'] = top
            elif player == 2:
                game_state['paddle2']['top'] = top

            self.broadcast_game_state()

        elif data['type'] == 'ball_update':
            self.update_ball_position(game_state)

    def broadcast_game_state(self):
        """Send the current game state to all players."""
        game_state = self.channel_layer.game_state[self.room_group_name]
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'update_game_state',
                'state': game_state
            }
        )

    def update_game_state(self, event):
        """Send updated game state to the client."""
        self.send(text_data=json.dumps({
            'type': 'game_state',
            'state': event['state']
        }))

    def initialize_game_state(self):
        """Initialize or reset the game state."""
        return {
            'ball': {'top': 50, 'left': 50},
            'paddle1': {'top': 50},
            'paddle2': {'top': 50},
            'score1': 0,
            'score2': 0,
            'dx': 1,
            'dy': 1,
            'players_connected': 0,
            'status': 'waiting'
        }
