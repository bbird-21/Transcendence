const gameId = JSON.parse(document.getElementById("game_id").textContent);
const socket = new WebSocket(`ws://${window.location.host}/ws/play/${gameId}/`);

let gameState = "start";
let paddle_1 = document.querySelector(".paddle_1");
let paddle_2 = document.querySelector(".paddle_2");
let board = document.querySelector(".board");
let ball = document.querySelector(".ball");
let score_1 = document.querySelector(".player_1_score");
let score_2 = document.querySelector(".player_2_score");
let message = document.querySelector(".message");

let paddle_common = document.querySelector(".paddle").getBoundingClientRect();
let board_coord = board.getBoundingClientRect();
console.log(board_coord);

// Initial position for the ball (center of the board)
let initialBallPosition = { top: board_coord.height / 2 - ball.offsetHeight / 2, left: board_coord.width / 2 - ball.offsetWidth / 2 };

socket.onopen = () => console.log("WebSocket connection established");
socket.onclose = () => console.log("WebSocket connection closed");
socket.onerror = (error) => console.error("WebSocket error:", error);

let playerRole = null;

socket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    // Handle player role assignment
    if (data.type === "player_role") {
        playerRole = data.player_role;
        console.log(`You are Player ${playerRole}`);
        return;
    }

    // Check for game state updates
    if (data.state) {
        updateGameState(data.state);
    }

    gameState = "play";
    // startBallMovement();  // This is where the ball should start moving
};



function startBallMovement() {
    // Initial random velocity and direction for ball
    dx = Math.floor(Math.random() * 4) + 3;
    dy = Math.floor(Math.random() * 4) + 3;
    dxd = Math.floor(Math.random() * 2);
    dyd = Math.floor(Math.random() * 2);
    
    requestAnimationFrame(() => {
        moveBall(dx, dy, dxd, dyd);
    });
}

function moveBall(dx, dy, dxd, dyd) {
    const ballPosition = ball.getBoundingClientRect();
    const boardRect = board.getBoundingClientRect();

    const ballTopPercent = parseFloat(ball.style.top || 50); // Default to 50% (centered)
    const ballLeftPercent = parseFloat(ball.style.left || 50);

    const newTopPercent = ballTopPercent + dy * (dyd === 0 ? 1 : -1); // Move by percentage
    const newLeftPercent = ballLeftPercent + dx * (dxd === 0 ? 1 : -1);

    // Check collisions
    if (newTopPercent <= 0 || newTopPercent >= 100) {
        dyd = 1 - dyd; // Reverse direction
    }

    // Paddle collision detection (adjust to percentages)
    const paddle1TopPercent = (paddle_1.offsetTop / boardRect.height) * 100;
    const paddle2TopPercent = (paddle_2.offsetTop / boardRect.height) * 100;
    const paddleHeightPercent = (paddle_common.height / boardRect.height) * 100;

    if (
        newLeftPercent <= 2 && // Close to left wall (adjust for paddle width)
        ballTopPercent >= paddle1TopPercent &&
        ballTopPercent <= paddle1TopPercent + paddleHeightPercent
    ) {
        dxd = 1; // Bounce right
    }

    if (
        newLeftPercent >= 98 && // Close to right wall
        ballTopPercent >= paddle2TopPercent &&
        ballTopPercent <= paddle2TopPercent + paddleHeightPercent
    ) {
        dxd = 0; // Bounce left
    }

    // Update ball position in percentages
    ball.style.top = `${Math.max(0, Math.min(100, newTopPercent))}%`;
    ball.style.left = `${Math.max(0, Math.min(100, newLeftPercent))}%`;

    requestAnimationFrame(() => moveBall(dx, dy, dxd, dyd)); // Continue moving
}


// This will trigger when either player presses Enter to start the game
document.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && gameState === "start") {
        gameState = "play";  // Set the game state to play
        socket.send(JSON.stringify({ type: "start_game" }));  // Notify the server to start the game
        message.innerHTML = "Game Started";  // Update the message on the player's screen
        message.style.left = 42 + 'vw';  // Adjust the position (if necessary)
    }

    // Handle paddle movement once the game has started
    if (gameState === "play") {
        // console.log(e);
        if (e.key === "w" || e.key === "W") {
            movePaddle(1, -1);
        } else if (e.key === "s" || e.key === "S" ) {
            movePaddle(1, 1);
        } else if (e.key === "ArrowUp") {
            movePaddle(2, -1);
        } else if (e.key === "ArrowDown") {
            movePaddle(2, 1);
        }
    }
});

function movePaddle(player, direction) {
    if (playerRole !== player) {
        // Ignore movement if the player tries to move the other paddle
        return;
    }

    const paddle = player === 1 ? paddle_1 : paddle_2;
    const boardHeight = board_coord.height;

    // Get the current top position of the paddle relative to the board
    let currentTopPx = paddle.getBoundingClientRect().top - board_coord.top;

    // Calculate the new position in pixels
    const moveAmountPx = direction * 0.05 * boardHeight; // Move by 5% of the board height
    let newTopPx = currentTopPx + moveAmountPx;

    // Constrain the paddle's position to stay within the board
    const paddleHeight = paddle_common.height;
    newTopPx = Math.max(0, Math.min(boardHeight - paddleHeight, newTopPx));

    // Update the paddle's position (convert back to % for style)
    const newTopPercent = (newTopPx / boardHeight) * 100;
    paddle.style.top = `${newTopPercent}%`;

    // Notify the server of paddle movement
    socket.send(
        JSON.stringify({
            type: "move_paddle",
            player: player,
            top: newTopPercent, // Send the relative position in %
        })
    );
    console.log(`Player: ${player}, Direction: ${direction}, Current Top (px): ${currentTopPx}, New Top (px): ${newTopPx}, New Top (%): ${newTopPercent}%`);
}


function updateGameState(state) {
    // Update paddle positions
    paddle_1.style.top = `${state.paddle1.top}%`;
    paddle_2.style.top = `${state.paddle2.top}%`;

    // Update ball position
    ball.style.top = `${state.ball.top}%`;
    ball.style.left = `${state.ball.left}%`;

    // Update scores
    score_1.innerHTML = state.score1;
    score_2.innerHTML = state.score2;

    // Reset ball to the center when game starts
    if (state.status === "start") {
        ball.style.top = "50%";
        ball.style.left = "50%";
    }
}

function updatePaddleSize() {
    const boardHeight = board_coord.height; // Current board height
    const paddleHeight = 0.2 * boardHeight; // Paddle height will be 10% of the board height

    // Update the paddle height using inline style
    paddle_1.style.height = `${paddleHeight}px`;
    paddle_2.style.height = `${paddleHeight}px`;

    // Update the bounding rectangle of the paddles to ensure proper handling later
    paddle_common = paddle_1.getBoundingClientRect();
}

// Make sure to update the paddle size when the page loads and when the window is resized
window.addEventListener('resize', () => {
    // Delay the recalculation slightly to avoid interference with other updates
    setTimeout(() => {
        board_coord = board.getBoundingClientRect();
        updatePaddleSize();
    }, 50);  // Adjust delay if needed
});

// Initialize paddle size on page load
updatePaddleSize();
