const gameId = JSON.parse(document.getElementById("game_id").textContent);
const countdown = document.getElementById("countdown");

// WebSocket connection
const socket = new WebSocket(`ws://${window.location.host}/ws/waiting_game/${gameId}/`);
// Variables to track button status
let isPlayerOneReady = false;
let isPlayerTwoReady = false;

document.addEventListener("DOMContentLoaded", () => {
    const playerOneButton = document.getElementById("player-one-button");
    const playerTwoButton = document.getElementById("player-two-button");

    // Disable buttons if the player is ready

    if (currentPlayer === "player_one") playerTwoButton.disabled = true;
    else if (currentPlayer === "player_two") playerOneButton.disabled = true;

    if (isPlayerOneReady) playerOneButton.disabled = true;
    if (isPlayerTwoReady) playerTwoButton.disabled = true;


    socket.onopen = () => {
        if (currentPlayer === "player_one" ) {
            if (playerOneButton) playerOneButton.disabled = false;
        } else {
            if (playerTwoButton) playerTwoButton.disabled = false;
        }
    };
    // Ensure buttons exist in the DOM and are only clickable by the right player
    if (playerOneButton) {
        playerOneButton.addEventListener("click", () => handleReadyButton("player_one"));
    }
    if (playerTwoButton) {
        playerTwoButton.addEventListener("click", () => handleReadyButton("player_two"));
    }
    
});

// Prevent a player from clicking the "Ready?" button multiple times or for the other player
function handleReadyButton(player) {
    const button = player === "player_one"
        ? document.getElementById("player-one-button")
        : document.getElementById("player-two-button");
    console.log(player)
    // If the button is already "Ready!", do nothing
    if (button.textContent === "Ready!") return;

    // Change button appearance and disable it
    if (button) {
        button.classList.add("ready");
        button.textContent = "Ready!";
        button.disabled = true;  // Disable button once clicked
    }

    // Send WebSocket message
    socket.send(JSON.stringify({
        type: "ready",
        player: player,
        ready: true  // The player is ready
    }));
}

// WebSocket message handler for updates from the server
socket.onmessage = function (event) {
    const message = JSON.parse(event.data);

    if (message.type === "current_state") {
        const playerOneButton = document.getElementById("player-one-button");
        const playerTwoButton = document.getElementById("player-two-button");

        // Update button states based on readiness
        if (message.player_one_ready && playerOneButton) {
            playerOneButton.classList.add("ready");
            playerOneButton.textContent = "Ready!";
            playerOneButton.disabled = true;
        }
        if (message.player_two_ready && playerTwoButton) {
            playerTwoButton.classList.add("ready");
            playerTwoButton.textContent = "Ready!";
            playerTwoButton.disabled = true;
        }
    }

    if (message.type === "ready_state") {
        const playerButton = message.player === "player_one"
            ? document.getElementById("player-one-button")
            : document.getElementById("player-two-button");

        if (playerButton) {
            playerButton.classList.add("ready");
            playerButton.textContent = "Ready!";
            playerButton.disabled = true;
        }
    }

    if (message.type === "player_disconnected") {
        const playerDisconnected = message.player;
        const playerOneButton = document.getElementById("player-one-button");
        const playerTwoButton = document.getElementById("player-two-button");

        if (playerDisconnected === "player_one" && playerOneButton) {
            playerOneButton.classList.remove("ready");
            playerOneButton.disabled = true;
        } else if (playerDisconnected === "player_two" && playerTwoButton) {
            playerTwoButton.classList.remove("ready");
            playerTwoButton.disabled = true;
        }
    }

    if (message.type === "start_countdown") {
        startCountdown();
    }
};


// Function to start the countdown when both players are ready
function startCountdown() {
    let timeLeft = 3;  // 3-second countdown
    countdown.textContent = timeLeft;

    const interval = setInterval(() => {
        timeLeft -= 1;
        countdown.textContent = timeLeft;

        if (timeLeft <= 0) {
            clearInterval(interval);
            // You can start the game here, or redirect to a new page
            console.log("Game starting!");
        }
    }, 1000);
}
