from channels.generic.websocket import WebsocketConsumer  # type: ignore
import json
from asgiref.sync import async_to_sync
from game.models import Invitation
import random
from .models import Game

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

        # Authenticate the user
        user = self.scope['user']
        if not user.is_authenticated:
            print("Unauthenticated user tried to connect.")
            self.close()
            return

        # Validate the GameID and check if the user is a valid player

        try:
            # Fetch the game from the database
            game = Game.objects.get(id=self.game_id)
            # Check if the user is either player_one or player_two
            if not (user == game.player_one or user == game.player_two):
                self.close()
                return
        except Game.DoesNotExist:
            print(f"Game with ID {self.game_id} does not exist.")
            # return False

        print(f"Connecting player {user.username} to game {self.game_id}")

        # Initialize game state if it doesn't exist
        if not hasattr(self.channel_layer, "game_state"):
            self.channel_layer.game_state = {}

        if self.room_group_name not in self.channel_layer.game_state:
            print(f"Initializing game state for {self.room_group_name}")
            self.channel_layer.game_state[self.room_group_name] = self.initialize_game_state()

        # Add the player to the group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        # Assign roles
        game_state = self.channel_layer.game_state[self.room_group_name]
        if 'player1_channel' not in game_state:
            game_state['player1_channel'] = self.channel_name
            self.player_role = 1
        elif 'player2' not in game_state:
            game_state['player2'] = user.username
            game_state['player2_channel'] = self.channel_name
            self.player_role = 2
        else:
            # If both players are already connected, reject this connection
            self.close()
            return

        # Notify the player of their role
        self.send(text_data=json.dumps({
            'type': 'player_role',
            'player_role': self.player_role
        }))

        print(f"Player {self.player_role} ({user.username}) connected.")

        # Update the players_connected count
        game_state['players_connected'] += 1

        # If both players are connected, start the game
        if game_state['players_connected'] == 2:
            self.start_game()

        # Broadcast the current game state to the connected player
        self.broadcast_game_state()


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
        game_state = self.channel_layer.game_state[self.room_group_name]
        
        # Ball starts at the center of the board in percentage terms
        game_state['ball'] = {'top': 50, 'left': 50}
        game_state['paddle1'] = {'top': 50}  # Percent from the top
        game_state['paddle2'] = {'top': 50}
        game_state['dx'] = 2  # Move by 2% increments
        game_state['dy'] = 2
        game_state['status'] = 'playing'

        self.broadcast_game_state()

    def update_ball_position(self, game_state):
        ball = game_state['ball']
        dx = game_state['dx']
        dy = game_state['dy']

        ball['top'] += dy
        ball['left'] += dx

        # Check for wall collisions
        if ball['top'] <= 0 or ball['top'] >= 100:
            game_state['dy'] *= -1  # Reverse direction

        # TODO: Add paddle collision logic


    def receive(self, text_data):
        """Handle incoming messages."""
        data = json.loads(text_data)
        game_state = self.channel_layer.game_state[self.room_group_name]

        if data['type'] == 'move_paddle':
            player = data['player']
            top = data['top']

            # Verify that the player is controlling their assigned paddle
            if (player == 1 and self.channel_name != game_state.get('player1_channel')) or \
            (player == 2 and self.channel_name != game_state.get('player2_channel')):
                print(f"Invalid paddle control attempt by player {player}")
                return

            # Enforce boundaries (0% to 100% - paddle height in %)
            paddle_height_percentage = 20  # Assuming paddles are 20% of the board height
            top = max(0, min(100 - paddle_height_percentage, top))

            # Update the server-side paddle position
            if player == 1:
                game_state['paddle1']['top'] = top
            elif player == 2:
                game_state['paddle2']['top'] = top

            # Debug: Log the new paddle position
            print(f"Player {player} paddle updated to {top}%")

            # Broadcast the updated game state
            self.broadcast_game_state()



    def broadcast_game_state(self):
        try:
            game_state = self.channel_layer.game_state[self.room_group_name]
            # Ensure game state is JSON serializable
            json.dumps(game_state)  # This will raise an error if it's not
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_game_state',
                    'state': game_state,
                }
            )
        except Exception as e:
            print(f"Error in broadcast_game_state: {e}")
            self.close()

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
