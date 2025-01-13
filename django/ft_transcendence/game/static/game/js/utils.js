
function addPlayersName(playerOne, playerTwo, round) {
	console.log('Add Player Name')
	const player1Element = document.querySelector('.player_1_username');
	const player2Element = document.querySelector('.player_2_username');

	player1Element.textContent = playerOne
	player2Element.textContent = playerTwo

}
