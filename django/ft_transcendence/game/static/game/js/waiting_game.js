const gameID = JSON.parse(document.getElementById('game_id').textContent);

const chatSocket = new WebSocket(
	'ws://'
	+ window.location.host
	+ '/ws/waiting_game/'
	+ gameID
	+ '/'
);

chatSocket.onclose = function(e) {
	console.error('Chat socket closed unexpectedly');
};
