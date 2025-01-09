// Get all buttons with the "social-bar--buttons" class
const socialButtons = document.querySelectorAll('.social-bar--buttons');

// Get the Friends button specifically
const friendsButton = document.querySelector('.social-bar--friends .social-bar--buttons');

// Get the container where the information will be displayed
const infoContainer = document.getElementById('infoContainer');

// Function to load the corresponding template based on button click
function loadContent(templateId) {
	const template = document.getElementById(templateId);
	if (template) {
		// Clone template's content and display it in the container
		const content = template.content.cloneNode(true);
		infoContainer.innerHTML = ''; // Clear existing content
		infoContainer.appendChild(content); // Add new content to the container
	}
}

// Function to handle button clicks and update the content
function handleButtonClick(event) {
	// Remove 'buttons-active' class from all buttons and reset images
	socialButtons.forEach(button => {
		button.classList.remove('buttons-active');
		const imgElement = button.querySelector('img');
		const originalSrc = button.getAttribute('data-img-original');
		if (imgElement && originalSrc) {
			imgElement.src = originalSrc;
		}
	});

	// Add 'buttons-active' class to clicked button and update image
	const clickedButton = event.currentTarget;
	clickedButton.classList.add('buttons-active');
	const imgElement = clickedButton.querySelector('img');
	const clickedImgSrc = clickedButton.getAttribute('data-img-clicked');
	if (imgElement && clickedImgSrc) {
		imgElement.src = clickedImgSrc;
		imgElement.classList.add('icons-logos');
	}

	// Load the corresponding template based on data-info attribute
	const dataType = clickedButton.getAttribute('data-info');
	if (dataType === 'all_friends') {
		loadContent('all-friends-template');
	} else if (dataType === 'pending_requests') {
		loadContent('pending-requests-template');
	} else if (dataType === 'blocked_users') {
		loadContent('blocked-users-template');
	}
}

// Store original image source for each button and add click listeners
socialButtons.forEach(button => {
	const imgElement = button.querySelector('img');
	if (imgElement) {
		button.setAttribute('data-img-original', imgElement.src);
	}
	button.addEventListener('click', handleButtonClick);
});

// Load the Friends section by default on page load and mark the button as active
window.addEventListener('DOMContentLoaded', () => {
	loadContent('all-friends-template'); // Load Friends content
	friendsButton.classList.add('buttons-active'); // Mark Friends button as active

	// Change Friends button image to clicked version
	const imgElement = friendsButton.querySelector('img');
	const clickedImgSrc = friendsButton.getAttribute('data-img-clicked');
	if (imgElement && clickedImgSrc) {
		imgElement.src = clickedImgSrc;
		imgElement.classList.add('icons-logos');
	}
});

