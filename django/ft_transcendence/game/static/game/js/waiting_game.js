const gameId = JSON.parse(document.getElementById("game_id").textContent);
const playerOneButton = document.getElementById("player-one-button");
const playerTwoButton = document.getElementById("player-two-button");
const countdown = document.getElementById("countdown");

// WebSocket connection
const chatSocket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

chatSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === "update") {
        // Update button states
        if (data.player_one_ready) {
            playerOneButton.textContent = "Ready!";
            playerOneButton.classList.add("ready");
            playerOneButton.disabled = true;
        }
        if (data.player_two_ready) {
            playerTwoButton.textContent = "Ready!";
            playerTwoButton.classList.add("ready");
            playerTwoButton.disabled = true;
        }
    }

    // Start countdown when both players are ready
    if (data.type === "start_countdown") {
        startCountdown();
    }
};

// Notify the server when a player clicks their button
playerOneButton.addEventListener("click", () => {
    chatSocket.send(JSON.stringify({ type: "ready", player: "one" }));
});
playerTwoButton.addEventListener("click", () => {
    chatSocket.send(JSON.stringify({ type: "ready", player: "two" }));
});

// Countdown logic
function startCountdown() {
    countdown.style.display = "block";
    let timer = 3;
    const interval = setInterval(() => {
        countdown.textContent = timer;
        timer -= 1;

        if (timer < 0) {
            clearInterval(interval);
            window.location.href = `/game/start/${gameId}/`;
        }
    }, 1000);
}

chatSocket.onclose = function(e) {
	console.error('Chat socket closed unexpectedly');
};
