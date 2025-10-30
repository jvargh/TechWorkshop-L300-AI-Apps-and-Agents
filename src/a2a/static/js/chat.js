class ProductManagementAgentChat {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.isTyping = false;
        this.messageHistory = [];
        
        this.initializeElements();
        this.attachEventListeners();
        this.updateStatus('connected');
        this.autoResizeTextarea();
    }

    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.messagesContainer = document.getElementById('messages');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.welcomeMessage = document.getElementById('welcome-message');
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');
        this.charCount = document.getElementById('char-count');
        this.newConversationBtn = document.getElementById('new-conversation-btn');
    }

    attachEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // New conversation button click
        this.newConversationBtn.addEventListener('click', () => this.startNewConversation());
        
        // Enter key to send (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input validation and character counter
        this.messageInput.addEventListener('input', () => {
            this.updateSendButton();
            this.updateCharCounter();
            this.autoResizeTextarea();
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('paste', () => {
            setTimeout(() => this.autoResizeTextarea(), 0);
        });
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    startNewConversation() {
        // Generate new session ID
        this.sessionId = this.generateSessionId();
        
        // Clear message history
        this.messageHistory = [];
        
        // Clear chat messages
        this.messagesContainer.innerHTML = '';
        
        // Show welcome message again
        this.welcomeMessage.style.display = 'block';
        
        // Clear input
        this.messageInput.value = '';
        this.updateSendButton();
        this.updateCharCounter();
        this.autoResizeTextarea();
        
        // Hide typing indicator
        this.typingIndicator.style.display = 'none';
        this.isTyping = false;
        
        console.log('Started new conversation with session ID:', this.sessionId);
    }

    updateStatus(status) {
        const statusMap = {
            'connecting': { text: 'Connecting...', class: '' },
            'connected': { text: 'Online', class: 'connected' },
            'error': { text: 'Connection Error', class: 'error' }
        };
        
        const statusInfo = statusMap[status] || statusMap['connecting'];
        this.statusText.textContent = statusInfo.text;
        this.statusIndicator.className = `status-indicator ${statusInfo.class}`;
    }

    formatMarkdown(text) {
        // Simple markdown to HTML converter for basic formatting
        let formatted = text
            // Convert headers
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            // Convert bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Convert italic text
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Convert bullet points
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            // Convert line breaks
            .replace(/\n/g, '<br>');
            
        // Wrap consecutive list items in <ul> tags
        formatted = formatted.replace(/(<li>.*?<\/li>(?:\s*<br>\s*<li>.*?<\/li>)*)/g, '<ul>$1</ul>');
        
        // Clean up extra <br> tags around lists
        formatted = formatted.replace(/<br>\s*<ul>/g, '<ul>').replace(/<\/ul>\s*<br>/g, '</ul>');
        
        return formatted;
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isTyping;
    }

    updateCharCounter() {
        const length = this.messageInput.value.length;
        this.charCount.textContent = length;
        
        if (length > 1800) {
            this.charCount.style.color = 'var(--error-color)';
        } else if (length > 1500) {
            this.charCount.style.color = 'var(--warning-color)';
        } else {
            this.charCount.style.color = 'var(--text-muted)';
        }
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // Hide welcome message on first interaction
        if (this.welcomeMessage) {
            this.welcomeMessage.style.display = 'none';
        }

        // Add user message
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        this.updateSendButton();
        this.updateCharCounter();
        this.autoResizeTextarea();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            await this.getAgentResponse(message);
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I encountered an error while processing your request. Please try again.', 'assistant', true);
        } finally {
            this.hideTypingIndicator();
        }
    }

    async getAgentResponse(message) {
        try {
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Add assistant response
            this.addMessage(data.response, 'assistant');
            
            // Update session ID if provided
            if (data.session_id) {
                this.sessionId = data.session_id;
            }
            
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    addMessage(content, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        
        // Convert markdown-style formatting to HTML for assistant messages
        if (sender === 'assistant') {
            textDiv.innerHTML = this.formatMarkdown(content);
        } else {
            textDiv.textContent = content;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        
        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        if (isError) {
            contentDiv.style.background = 'var(--error-color)';
            contentDiv.style.color = 'white';
        }
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store in history
        this.messageHistory.push({ sender, content, timestamp: new Date() });
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.updateSendButton();
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
        this.updateSendButton();
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    clearSession() {
        this.messageHistory = [];
        this.messagesContainer.innerHTML = '';
        this.sessionId = this.generateSessionId();
        if (this.welcomeMessage) {
            this.welcomeMessage.style.display = 'block';
        }
    }
}

// Global functions for example buttons
function sendExample(button) {
    const message = button.textContent.replace(/"/g, '');
    const chat = window.productChat;
    if (chat) {
        chat.messageInput.value = message;
        chat.sendMessage();
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.productChat = new ProductManagementAgentChat();
    
    // Test connectivity
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            console.log('Health check:', data);
            window.productChat.updateStatus('connected');
        })
        .catch(error => {
            console.error('Health check failed:', error);
            window.productChat.updateStatus('error');
        });
});

// Handle visibility change to pause/resume when tab is not active
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, can pause timers or reduce activity
    } else {
        // Page is visible, can resume full functionality
        if (window.productChat) {
            window.productChat.scrollToBottom();
        }
    }
});

// Handle browser resize
window.addEventListener('resize', () => {
    if (window.productChat) {
        window.productChat.scrollToBottom();
    }
});
