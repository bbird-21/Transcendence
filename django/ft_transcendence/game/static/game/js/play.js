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

// Initial position for the ball (center of the board)
let initialBallPosition = { top: board_coord.height / 2 - ball.offsetHeight / 2, left: board_coord.width / 2 - ball.offsetWidth / 2 };

socket.onopen = () => console.log("WebSocket connection established");
socket.onclose = () => console.log("WebSocket connection closed");
socket.onerror = (error) => console.error("WebSocket error:", error);
socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    

    // Check for game state updates
    if (data.game_state) {
        updateGameState(data.game_state);
    }

    // If the game is started, update the UI and start the game logic
    if (data.game_state && data.game_state.status === 'playing') {
        gameState = 'play';
        message.innerHTML = 'Game Started';
        message.style.left = 42 + 'vw';
        startBallMovement();  // Start the ball movement after game starts
    }
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


// Start Game on Enter key press
document.addEventListener("keydown", (e) => {

    if (gameState === "play") {
        if (e.key === "w") {
            movePaddle(1, -1);
        } else if (e.key === "s") {
            movePaddle(1, 1);
        } else if (e.key === "ArrowUp") {
            movePaddle(2, -1);
        } else if (e.key === "ArrowDown") {
            movePaddle(2, 1);
        }
    }

    if (e.key === "Enter" && gameState === "start") {
        gameState = "play";
        socket.send(JSON.stringify({ type: "start_game" }));
        message.innerHTML = "Game Started";
    }
});

function movePaddle(player, direction) {
    
    const paddle = player === 1 ? paddle_1 : paddle_2;
    const currentCoord = paddle.getBoundingClientRect();
    const newTop = Math.max(
        board.getBoundingClientRect().top,
        Math.min(
            board.getBoundingClientRect().bottom - paddle_common.height,
            currentCoord.top + direction * window.innerHeight * 0.05
        )
    );
    paddle.style.top = newTop + "px";

    // Notify server of paddle movement
    socket.send(
        JSON.stringify({
            type: "move_paddle",
            player: player,
            top: newTop - board.getBoundingClientRect().top, // Relative to board
        })
    );
}

function updateGameState(state) {
    paddle_1.style.top = board.getBoundingClientRect().top + state.paddle1.top + "px";
    paddle_2.style.top = board.getBoundingClientRect().top + state.paddle2.top + "px";
    ball.style.top = board.getBoundingClientRect().top + state.ball.top + "px";
    ball.style.left = board.getBoundingClientRect().left + state.ball.left + "px";
    score_1.innerHTML = state.score1;
    score_2.innerHTML = state.score2;

    // Reset ball to the center when game starts
    if (state.status === "start") {
        ball.style.top = `${board.getBoundingClientRect().top + initialBallPosition.top}px`;
        ball.style.left = `${board.getBoundingClientRect().left + initialBallPosition.left}px`;
    }
}