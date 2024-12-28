
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');


function sendMessage() {
    const messageText = userInput.value.trim();
    if (messageText === '') return;

    
    const userMessage = document.createElement('div');
    userMessage.classList.add('user-message');
    userMessage.innerHTML = `<p>${messageText}</p>`;
    chatMessages.appendChild(userMessage);

    
    userInput.value = '';

    
    chatMessages.scrollTop = chatMessages.scrollHeight;

    
    setTimeout(() => {
        const botMessage = document.createElement('div');
        botMessage.classList.add('bot-message');
        botMessage.innerHTML = `<p>I'm here to help! Please elaborate on your query.</p>`;
        chatMessages.appendChild(botMessage);

        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 1000);
}