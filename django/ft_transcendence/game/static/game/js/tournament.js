const playerOneInput = document.getElementById('player-one')
const playerTwoInput = document.getElementById('player-two')
const playerThreeInput = document.getElementById('player-three')
const playerFourInput = document.getElementById('player-four')

saveButton.addEventListener('click', () => {
	const playerOne = playerOneInput.value;
	const playerTwo = playerTwoInput.value;
	const playerThree = playerThreeInput.value;
	const playerFour = playerFourInput.value;

	console.log(`playerOne : ${playerOne}`)
});
