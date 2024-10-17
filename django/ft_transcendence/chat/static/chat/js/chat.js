const roomName = JSON.parse(document.getElementById('room-name').textContent);
const userID   = JSON.parse(document.getElementById('userID').textContent);

const chatSocket = new WebSocket(
	'ws://'
	+ window.location.host
	+ '/ws/chat/'
	+ roomName
	+ '/'
	+ userID
	+ '/'

);

chatSocket.onmessage = function (e) {
	const data = JSON.parse(e.data);
	document.querySelector('#chat-log').value += (data.message + '\n');
};

chatSocket.onclose = function (e) {
	console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
	if (e.key === 'Enter') {  // enter, return
		document.querySelector('#chat-message-submit').click();
	}
};

document.querySelector('#chat-message-submit').onclick = function(e) {
	const messageInputDom = document.querySelector('#chat-message-input');
	const message = messageInputDom.value;
	chatSocket.send(JSON.stringify({
		"message": message,
		"refChat" : roomName,
		"author" : userID,
		"type" : 0,
		"extraData" : ""
	}));
	messageInputDom.value = '';
};
