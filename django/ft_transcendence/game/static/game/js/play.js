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

let round = 0;
let winners = [];

if ( tournament === true ) {
    startTournament();
    const players = getTournamentPlayers();
    addPlayersName(players.playerOne, players.playerTwo, 0);
}
else {
    playRound();
}

function createHandleKeydown(resolve) {
    return function handleKeydown(e) {
        if (e.key === "Enter") {
            gameState = gameState === "start" ? "play" : "start";
            if (gameState === "play") {
                console.log(`round ${round}`)
                message.innerHTML = "Game Started";
                message.style.left = 42 + "vw";
                requestAnimationFrame(() => {
                    dx = Math.floor(Math.random() * 4) + 3;
                    dy = Math.floor(Math.random() * 4) + 3;
                    dxd = Math.floor(Math.random() * 2);
                    dyd = Math.floor(Math.random() * 2);
                    moveBall(dx, dy, dxd, dyd, handleKeydown);

                });
            }
            resolve(); // Resolve the promise for Enter key
        } else if (gameState === "play") {
            if (e.key === "w") {
                paddle_1.style.top = Math.max(
                    board_coord.top,
                    paddle_1_coord.top - window.innerHeight * 0.06
                ) + "px";
                paddle_1_coord = paddle_1.getBoundingClientRect();
            }
            if (e.key === "s") {
                paddle_1.style.top = Math.min(
                    board_coord.bottom - paddle_common.height,
                    paddle_1_coord.top + window.innerHeight * 0.06
                ) + "px";
                paddle_1_coord = paddle_1.getBoundingClientRect();
            }

            if (e.key === "ArrowUp") {
                paddle_2.style.top = Math.max(
                    board_coord.top,
                    paddle_2_coord.top - window.innerHeight * 0.1
                ) + "px";
                paddle_2_coord = paddle_2.getBoundingClientRect();
            }
            if (e.key === "ArrowDown") {
                paddle_2.style.top = Math.min(
                    board_coord.bottom - paddle_common.height,
                    paddle_2_coord.top + window.innerHeight * 0.1
                ) + "px";
                paddle_2_coord = paddle_2.getBoundingClientRect();
            }
        }
    };
}

async function playRound() {

    // Function to wait for a key press
    const waitForKeyPress = () => {
        return new Promise((resolve) => {
            const keydownHandler = createHandleKeydown(resolve); // Create a specific handler
            document.addEventListener("keydown", keydownHandler);
        });
    };

    // Wait for the Enter key press to start the game
    await waitForKeyPress();
    console.log("Round started");
    return 0;
}

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
        if ( score_1.innerHTML === '1' || score_2.innerHTML === '1') {
            showVictoryMessage();
            return;
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

    // Continue animating
    requestAnimationFrame(() => {
        moveBall(dx, dy, dxd, dyd);
        if ( score_1.innerHTML == '1' || score_2.innerHTML == '1')
            tournamentStrategy();
    });
}

function tournamentStrategy() {
    if ( round == 0 ) {
        if ( score_1.innerHTML == '1' )
            winners.push(players.playerOne)
        else if ( score_2.innerHTML == '1')
            winners.push(players.playerTwo)
        addPlayersName(players.playerThree, players.playerFour, round)
    }
    else if ( round == 1 ) {
        if ( score_1.innerHTML == '1' )
            winners.push(players.playerThree);
        else if ( score_2.innerHTML == '1' )
            winners.push(players.playerFour);
        addPlayersName(winners[0], winners[1], round)

    }
    else if ( round == 2 ) {
        if ( score_1.innerHTML == '1' ) {
            showVictoryMessage(winners[0]);
        }
        else if ( score_2.innerHTML == '1' ) {
            showVictoryMessage(winners[1]);
        }
        addVictoryButtons();
    }
    score_1.innerHTML = '0'
    score_2.innerHTML = '0'
    round++;
}

function victoryStrategy() {
    if ( round == 0 ) {
        winners.push(players.playerOne)
    }
    round++;
    score_1.innerHTML = '0'
    score_2.innerHTML = '0'
}
function showVictoryMessage(winner) {
    if (document.querySelector('.victory-overlay')) {
        return;
    }

    // Create the overlay div
    const overlayDiv = document.createElement('div');
    overlayDiv.classList.add('victory-overlay');

    // Create the victory message div
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('victory-message');

    // Add the victory text
    const victoryText = document.createElement('h1');
    victoryText.textContent = `${winner} Wins!`;
    victoryText.classList.add('victory-text');
    messageDiv.appendChild(victoryText);

    // Add the victory image
    const victoryImage = document.createElement('img');
    victoryImage.src = victoryImagePath; // Use the path passed from the Django template
    victoryImage.alt = 'Victory';
    victoryImage.classList.add('victory-image');
    messageDiv.appendChild(victoryImage);

    // Append the message div to the overlay
    overlayDiv.appendChild(messageDiv);

    // Add the overlay to the body
    document.body.appendChild(overlayDiv);

    if (tournament === true) {
        addVictoryButtons(messageDiv);
    }

    // Use a slight delay to ensure the animation is visible
    setTimeout(() => {
        victoryImage.classList.add('appear'); // Trigger animation
    }, 10);
}

function addVictoryButtons(messageDiv) {

	console.log('add victory buttons')
    // Add "Home" button
    const homeButton = document.createElement('button');
    homeButton.innerText = 'Home';
    homeButton.onclick = () => {
      window.location.href = homeUrl; // Use the URL passed from the Django template
    };
    homeButton.classList.add('victory-button'); // Add styles

    // Add "Play Again" button
    const playButton = document.createElement('button');
    playButton.innerText = 'Play Again';
    playButton.onclick = () => {
      window.location.href = playUrl; // Use the URL passed from the Django template
    };
    playButton.classList.add('victory-button'); // Add styles

    // Append buttons to the message div
    messageDiv.appendChild(homeButton);
    messageDiv.appendChild(playButton);

}
