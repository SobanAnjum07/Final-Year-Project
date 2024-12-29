document.getElementById('chat-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (!message) return;

    const chatMessages = document.getElementById('chat-messages');

    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'user-message';
    userMessageDiv.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(userMessageDiv);

    userInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]').value,
                message: message,
            }),
        });

        const data = await response.json();
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'bot-message';
        botMessageDiv.innerHTML = `<p>${data.response}</p>`;
        chatMessages.appendChild(botMessageDiv);

        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
        console.error('Error:', error);
    }
});
