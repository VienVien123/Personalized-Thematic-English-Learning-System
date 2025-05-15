// Chatbot Functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotContainer = document.getElementById('chatbotContainer');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatbotInput = document.getElementById('chatbotInput');
    const chatbotSend = document.getElementById('chatbotSend');
    const chatbotMessages = document.getElementById('chatbotMessages');

    // Toggle chatbot visibility
    chatbotToggle.addEventListener('click', function() {
        chatbotContainer.classList.add('show');
    });

    // Close chatbot
    chatbotClose.addEventListener('click', function() {
        chatbotContainer.classList.remove('show');
    });

    // Send message
    // function sendMessage() {
    //     const message = chatbotInput.value.trim();
    //     if (message) {
    //         // Add user message
    //         addMessage(message, 'user');
    //         chatbotInput.value = '';

    //         // Simulate bot response
    //         setTimeout(() => {
    //             const responses = [
    //                 "I understand. Could you tell me more about that?",
    //                 "That's interesting! Let me help you with that.",
    //                 "I see. Here's what I can suggest...",
    //                 "Let me explain that in more detail.",
    //                 "I'll help you practice that."
    //             ];
    //             const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    //             addMessage(randomResponse, 'bot');
    //         }, 1000);
    //     }
    // }
async function sendMessage() {
    const message = chatbotInput.value.trim();
    if (message) {
        addMessage(message, 'user');
        chatbotInput.value = '';

        try {
            const res = await fetch('/api/chatbot/gemini/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    topic: 'Grammar' 
                })
            });

            const data = await res.json();
            if (data.response) {
                addMessage(data.response, 'bot');
            } else {
                addMessage("❌ Bot gặp lỗi khi trả lời.", 'bot');
            }
        } catch (error) {
            console.error(error);
            addMessage("❌ Lỗi khi kết nối bot.", 'bot');
        }
    }
}

    // Add message to chat
    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = text;
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Send message on button click
    chatbotSend.addEventListener('click', sendMessage);

    // Send message on Enter key
    chatbotInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Progress circle animation
    function animateProgressCircle(element, percent) {
        const circle = element.querySelector('.progress');
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        const offset = circumference - (percent / 100) * circumference;
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = offset;
    }

    // Initialize progress circles
    const progressCircles = document.querySelectorAll('.progress-circle');
    progressCircles.forEach(circle => {
        const percent = circle.getAttribute('data-percent');
        animateProgressCircle(circle, percent);
    });
}); 

function loadUserAvatar() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) return;

    const avatarImg = document.getElementById('user-avatar-img');
    const avatarInitial = document.getElementById('user-avatar-initial');
    const nameDisplay = document.getElementById('user-name-display');

    if (!avatarImg || !avatarInitial) return;
    if (nameDisplay) nameDisplay.textContent = user.name || user.email;

    if (user.avatar) {
        const baseUrl = window.location.origin;
        const url = user.avatar;
        avatarImg.src = url;

        avatarImg.onload = () => {
        avatarImg.style.display = 'block';
        avatarImg.style.zIndex = '1';
        avatarInitial.classList.add('d-none');  // ⬅ dùng class
        };

        avatarImg.onerror = () => {
        const initials = (user.name || user.email || 'U').slice(0, 2).toUpperCase();
        avatarInitial.textContent = initials;
        avatarInitial.classList.remove('d-none');
        avatarImg.style.display = 'none';
        };
    } else {
        const initials = (user.name || user.email || 'U').slice(0, 2).toUpperCase();
        avatarInitial.textContent = initials;
        avatarInitial.classList.remove('d-none');
        avatarImg.style.display = 'none';
    }
}
document.addEventListener('DOMContentLoaded', loadUserAvatar);