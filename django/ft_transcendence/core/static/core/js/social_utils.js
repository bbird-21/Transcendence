function showNotification(message) {
    const exception = document.getElementById('message_to_user');
    exception.textContent = message;
    exception.classList.remove('hidden');
    exception.classList.add('show');

    // Hide after 5 seconds
    setTimeout(() => {
        exception.classList.remove('show');
        setTimeout(() => exception.classList.add('hidden'), 500); // Allow transition to complete
    }, 5000);
}
