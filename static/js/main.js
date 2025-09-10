// Kochi Metro Induction System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeChatbot();
    initializeTooltips();
    initializeFileUploads();
    initializeFormValidation();
});

// Chatbot functionality
function initializeChatbot() {
    const chatToggle = document.getElementById('chat-toggle');
    const chatWidget = document.getElementById('chat-widget');
    const chatClose = document.getElementById('chat-close');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatMessages = document.getElementById('chat-messages');

    if (!chatToggle || !chatWidget) return;

    // Toggle chat widget
    chatToggle.addEventListener('click', function() {
        chatWidget.classList.add('active');
        chatInput.focus();
    });

    // Close chat widget
    chatClose.addEventListener('click', function() {
        chatWidget.classList.remove('active');
    });

    // Send message on button click
    chatSend.addEventListener('click', sendMessage);

    // Send message on Enter key
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessageToChat(message, 'user');
        chatInput.value = '';

        // Show typing indicator
        showTypingIndicator();

        // Send to backend
        fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator();
            if (data.success) {
                addMessageToChat(data.response, 'bot');
            } else {
                addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
            }
        })
        .catch(error => {
            console.error('Chat error:', error);
            hideTypingIndicator();
            addMessageToChat('Sorry, I\'m having trouble connecting. Please try again later.', 'bot');
        });
    }

    function addMessageToChat(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        messageElement.innerHTML = `
            <div class="message-content">${escapeHtml(message)}</div>
        `;
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.className = 'message bot-message typing-indicator';
        typingElement.innerHTML = `
            <div class="message-content">
                <span class="typing-dots">
                    <span></span><span></span><span></span>
                </span>
            </div>
        `;
        
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        const typingIndicator = chatMessages.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Custom ribbon tooltips
    const ribbons = document.querySelectorAll('.status-ribbon');
    ribbons.forEach(ribbon => {
        ribbon.addEventListener('mouseenter', function() {
            const tooltip = this.querySelector('.ribbon-tooltip');
            if (tooltip) {
                tooltip.style.opacity = '1';
                tooltip.style.visibility = 'visible';
            }
        });

        ribbon.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('.ribbon-tooltip');
            if (tooltip) {
                tooltip.style.opacity = '0';
                tooltip.style.visibility = 'hidden';
            }
        });
    });
}

// File upload functionality
function initializeFileUploads() {
    // General file upload handling
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file, input);
            }
        });
    });

    // Drag and drop for upload areas
    const uploadAreas = document.querySelectorAll('.upload-area, .upload-zone');
    
    uploadAreas.forEach(area => {
        area.addEventListener('dragover', handleDragOver);
        area.addEventListener('dragleave', handleDragLeave);
        area.addEventListener('drop', handleDrop);
    });

    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('dragover');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const fileInput = this.querySelector('input[type="file"]') || 
                            document.getElementById('file-input') ||
                            document.getElementById('certificate-upload');
            
            if (fileInput) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    }

    function validateFile(file, input) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = {
            'csv': ['.csv'],
            'excel': ['.xlsx', '.xls'],
            'document': ['.pdf', '.jpg', '.jpeg', '.png'],
            'certificate': ['.pdf', '.jpg', '.jpeg', '.png']
        };

        const inputType = input.id.includes('certificate') ? 'certificate' :
                         input.accept.includes('csv') ? 'csv' :
                         input.accept.includes('xlsx') ? 'excel' : 'document';

        const validTypes = allowedTypes[inputType] || allowedTypes.document;
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (file.size > maxSize) {
            showAlert('File size must be less than 10MB', 'warning');
            input.value = '';
            return false;
        }

        if (!validTypes.includes(fileExtension)) {
            showAlert(`Please select a valid file type: ${validTypes.join(', ')}`, 'warning');
            input.value = '';
            return false;
        }

        return true;
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });

    function validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                clearFieldError(field);
            }
        });

        // Email validation
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !isValidEmail(field.value)) {
                showFieldError(field, 'Please enter a valid email address');
                isValid = false;
            }
        });

        return isValid;
    }

    function showFieldError(field, message) {
        clearFieldError(field);
        field.classList.add('is-invalid');
        
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        errorElement.textContent = message;
        
        field.parentNode.appendChild(errorElement);
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }
}

// Utility functions
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showAlert(message, type = 'info') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertElement.style.top = '20px';
    alertElement.style.right = '20px';
    alertElement.style.zIndex = '9999';
    alertElement.style.minWidth = '300px';
    
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertElement);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.remove();
        }
    }, 5000);
}

// Loading state management
function showLoading(element, text = 'Loading...') {
    if (element.dataset.originalText === undefined) {
        element.dataset.originalText = element.innerHTML;
    }
    
    element.disabled = true;
    element.classList.add('loading');
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        ${text}
    `;
}

function hideLoading(element) {
    element.disabled = false;
    element.classList.remove('loading');
    if (element.dataset.originalText) {
        element.innerHTML = element.dataset.originalText;
    }
}

// Export functions for global access
window.MetroApp = {
    showAlert,
    showLoading,
    hideLoading,
    getCsrfToken,
    escapeHtml
};

// Add custom CSS for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-dots {
        display: inline-flex;
        gap: 3px;
    }
    
    .typing-dots span {
        width: 6px;
        height: 6px;
        background-color: #999;
        border-radius: 50%;
        animation: typingPulse 1.5s infinite;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typingPulse {
        0%, 60%, 100% {
            opacity: 0.3;
            transform: scale(0.8);
        }
        30% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .spinner-border-sm {
        width: 1rem;
        height: 1rem;
    }
`;
document.head.appendChild(style);