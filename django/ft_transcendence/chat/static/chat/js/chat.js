const roomName = JSON.parse(document.getElementById('room-name').textContent);
const userID = JSON.parse(document.getElementById('userID').textContent);
const receiverUsername = JSON.parse(document.getElementById('receiver_username').textContent);
const senderUsername = JSON.parse(document.getElementById('sender_username').textContent);

console.log(receiverUsername);
console.log(senderUsername);

const chatSocket = new WebSocket(
	'ws://' + window.location.host + '/ws/chat/' + roomName + '/' + userID + '/'
);

chatSocket.onopen = function(e) {
	fetchMessages();
}

chatSocket.onmessage = function(e) {
	const data = JSON.parse(e.data);
	if (data['command'] === 'messages') {
		for (let i = 0; i < data['messages'].length; i++) {
			createMessage(data['messages'][i], data['from']);
		}
	} else if (data['command'] === 'new_message') {
		createMessage(data['message'], data['from']);
	}
};

chatSocket.onclose = function(e) {
	console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
	if (e.key === 'Enter') {
		document.querySelector('#chat-message-submit').click();
	}
};

document.querySelector('#chat-message-submit').onclick = function(e) {
	const messageInputDom = document.querySelector('#chat-message-input');
	const message = messageInputDom.value;
	chatSocket.send(JSON.stringify({
		"message": message,
		"command": "new_message",
		"from": senderUsername,
		"refChat": roomName,
		"author": userID,
		"type": 0,
		"extraData": ""
	}));
	messageInputDom.value = '';
};

function fetchMessages() {
	chatSocket.send(JSON.stringify({
		'command': 'fetch_messages',
		'room_name': roomName
	}));
}

function createMessage(data, from) {
	const chatLog = document.querySelector('#chat-log');
	const messageElement = document.createElement('div');
	messageElement.classList.add('message');
	// Add class based on whether it's a sender or receiver
	if (from === senderUsername) {
		messageElement.classList.add('message-sender');
	} else {
		messageElement.classList.add('message-receiver');
	}

	// Add the content to the message box
	messageElement.textContent = data.content;
	chatLog.appendChild(messageElement);

	// Scroll to the latest message
	chatLog.scrollTop = chatLog.scrollHeight;
}
