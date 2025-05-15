document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        const res = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok) {
            // Lưu token và thông tin người dùng vào localStorage
            localStorage.setItem('access', data.access);
            localStorage.setItem('refresh', data.refresh);
            localStorage.setItem('user', JSON.stringify(data.user));

            // Gắn thông báo chào mừng để hiển thị sau khi chuyển trang
            localStorage.setItem('welcome_msg', `Chào mừng ${data.user.name || data.user.email} đã quay trở lại!`);
            
            // Chuyển hướng sang trang chủ
            window.location.href = '/';
        } else {
            alert(data.error || 'Login failed');
        }
    });
});