// game.js (client-side WebSocket connection)
const gameId = JSON.parse(document.getElementById("game_id").textContent);
console.log(`GameId: ${gameId}`);
const socket = new WebSocket(`ws://${window.location.host}/ws/play/${gameId}/`);

let gameState = 'start';
let paddle_1 = document.querySelector('.paddle_1');
let paddle_2 = document.querySelector('.paddle_2');
let board = document.querySelector('.board');
let initial_ball = document.querySelector('.ball');
let ball = document.querySelector('.ball');
let score_1 = document.querySelector('.player_1_score');
let score_2 = document.querySelector('.player_2_score');
let message = document.querySelector('.message');
let paddle_1_coord = paddle_1.getBoundingClientRect();
let paddle_2_coord = paddle_2.getBoundingClientRect();
let initial_ball_coord = ball.getBoundingClientRect();
let ball_coord = initial_ball_coord;
let board_coord = board.getBoundingClientRect();
let paddle_common =
    document.querySelector('.paddle').getBoundingClientRect();

let dx = Math.floor(Math.random() * 4) + 3;
let dy = Math.floor(Math.random() * 4) + 3;
let dxd = Math.floor(Math.random() * 2);
let dyd = Math.floor(Math.random() * 2);

socket.onopen = function() {
    console.log('WebSocket connection established');
};

socket.onclose = function() {
    console.log('WebSocket connection closed');
};

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.game_state) {
        // Update game state based on data received from the server
        updateGameState(data.game_state);
    }
};

document.addEventListener('keydown', (e) => {
    if (e.key == 'Enter') {
        gameState = gameState == 'start' ? 'play' : 'start';
        if (gameState == 'play') {
            message.innerHTML = 'Game Started';
            message.style.left = 42 + 'vw';
            requestAnimationFrame(() => {
                dx = Math.floor(Math.random() * 4) + 3;
                dy = Math.floor(Math.random() * 4) + 3;
                dxd = Math.floor(Math.random() * 2);
                dyd = Math.floor(Math.random() * 2);
                moveBall(dx, dy, dxd, dyd);
            });
        }
    }

    if (gameState == 'play') {
        if (e.key == 'w') {
            paddle_1.style.top =
                Math.max(
                    board_coord.top,
                    paddle_1_coord.top - window.innerHeight * 0.06
                ) + 'px';
            paddle_1_coord = paddle_1.getBoundingClientRect();
            sendGameState();
        }
        if (e.key == 's') {
            paddle_1.style.top =
                Math.min(
                    board_coord.bottom - paddle_common.height,
                    paddle_1_coord.top + window.innerHeight * 0.06
                ) + 'px';
            paddle_1_coord = paddle_1.getBoundingClientRect();
            sendGameState();
        }

        if (e.key == 'ArrowUp') {
            paddle_2.style.top =
                Math.max(
                    board_coord.top,
                    paddle_2_coord.top - window.innerHeight * 0.1
                ) + 'px';
            paddle_2_coord = paddle_2.getBoundingClientRect();
            sendGameState();
        }
        if (e.key == 'ArrowDown') {
            paddle_2.style.top =
                Math.min(
                    board_coord.bottom - paddle_common.height,
                    paddle_2_coord.top + window.innerHeight * 0.1
                ) + 'px';
            paddle_2_coord = paddle_2.getBoundingClientRect();
            sendGameState();
        }
    }
});

let lastTime = null; // To track the last frame's timestamp
let speedMultiplier = 0.7;
function moveBall(dx, dy, dxd, dyd) {
    const currentTime = performance.now(); // High-resolution time for accuracy

    if (!lastTime) {
        lastTime = currentTime;
    }

    // Time difference between frames in seconds
    const deltaTime = (currentTime - lastTime) / 1000;
    lastTime = currentTime;

    // Calculate movement relative to board size
    const baseSpeed = 0.5; // Adjust this for desired speed; it's a fraction of board size per second
    const velocityX = baseSpeed * board_coord.width * deltaTime * speedMultiplier;
    const velocityY = baseSpeed * board_coord.height * deltaTime * speedMultiplier;

    const movementX = velocityX * (dxd === 0 ? -1 : 1);
    const movementY = velocityY * (dyd === 0 ? -1 : 1);

    // Bounce off top and bottom
    if (ball_coord.top <= board_coord.top) {
        dyd = 1;
    }
    if (ball_coord.bottom >= board_coord.bottom) {
        dyd = 0;
    }

    // Bounce off paddles
    if (
        ball_coord.left <= paddle_1_coord.right &&
        ball_coord.top >= paddle_1_coord.top &&
        ball_coord.bottom <= paddle_1_coord.bottom
    ) {
        dxd = 1;
    }
    if (
        ball_coord.right >= paddle_2_coord.left &&
        ball_coord.top >= paddle_2_coord.top &&
        ball_coord.bottom <= paddle_2_coord.bottom
    ) {
        dxd = 0;
    }

    // Reset if ball goes out of bounds
    if (
        ball_coord.left <= board_coord.left ||
        ball_coord.right >= board_coord.right
    ) {
        if (ball_coord.left <= board_coord.left) {
            score_2.innerHTML = +score_2.innerHTML + 1;
        } else {
            score_1.innerHTML = +score_1.innerHTML + 1;
        }
        gameState = 'start';
        ball_coord = initial_ball_coord;
        ball.style = initial_ball.style;
        message.innerHTML = 'Press Enter to Play Pong';
        message.style.left = 38 + 'vw';
        lastTime = null; // Reset lastTime for the next round
        return;
    }

    // Move the ball
    ball.style.top = ball_coord.top + movementY + 'px';
    ball.style.left = ball_coord.left + movementX + 'px';
    ball_coord = ball.getBoundingClientRect();

    // Send the updated game state to the server
    sendGameState();

    // Continue animating
    requestAnimationFrame(() => {
        moveBall(dx, dy, dxd, dyd);
    });
}

function sendGameState() {
    const gameState = {
        ball: { top: ball_coord.top, left: ball_coord.left },
        paddle1: { top: paddle_1_coord.top },
        paddle2: { top: paddle_2_coord.top },
        score1: score_1.innerHTML,
        score2: score_2.innerHTML
    };

    socket.send(JSON.stringify({
        type: 'gameState',
        state: gameState
    }));
}

function updateGameState(data) {
    // Update game state based on the data received from the server
    if (data.ball) {
        ball.style.top = data.ball.top + 'px';
        ball.style.left = data.ball.left + 'px';
    }
    if (data.paddle1) {
        paddle_1.style.top = data.paddle1.top + 'px';
    }
    if (data.paddle2) {
        paddle_2.style.top = data.paddle2.top + 'px';
    }
    if (data.score1) {
        score_1.innerHTML = data.score1;
    }
    if (data.score2) {
        score_2.innerHTML = data.score2;
    }
}
