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
    if (isPlayerOneReady) {
        playerOneButton.disabled = true;
    }
    if (isPlayerTwoReady) {
        playerTwoButton.disabled = true;
    }

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
socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    
    // If both players are ready, handle countdown (if necessary)
    if (message.type === "ready_state") {
        const playerButton = message.player === "player_one"
            ? document.getElementById("player-one-button")
            : document.getElementById("player-two-button");
        
        // Update the other player's button (they're ready)
        if (playerButton) {
            playerButton.classList.add("ready");
            playerButton.textContent = "Ready!";
            playerButton.disabled = true;  // Disable button
        }
    }

    // If both players are ready, initiate the countdown
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
