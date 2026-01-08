document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const sendBtn = document.getElementById('send-btn');
    
    // Generate or retrieve thread_id
    let threadId = localStorage.getItem('agent_thread_id');
    if (!threadId) {
        threadId = crypto.randomUUID();
        localStorage.setItem('agent_thread_id', threadId);
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Add User Message
        appendMessage('user', message);
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;
        sendBtn.textContent = 'Sending...';

        try {
            const response = await fetch('/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    thread_id: threadId
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Add AI Message
            if (data.response) {
                appendMessage('ai', data.response);
            } else {
                appendMessage('ai', 'Something went wrong. Please try again.');
            }

        } catch (error) {
            console.error('Error:', error);
            appendMessage('ai', 'Sorry, I encountered an error. Please try again.');
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
            userInput.focus();
        }
    });

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
