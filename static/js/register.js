document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-form');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const password2 = document.getElementById('password2').value;

        const response = await fetch('/api/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type':'application/json',
            },
            body: JSON.stringify({
                name,
                email,
                password,
                password2
            })
        });

        const data = await response.json();

        if (response.ok) {
            // alert('Đăng ký thành công! Mời bạn đăng nhập.');
            window.location.href = '/login/';
        } else {
            let errorMsg = '';
            for (const key in data) {
                errorMsg += `${key}: ${data[key]}\n`;
            }
            alert('Lỗi đăng ký:\n' + errorMsg);
        }
    });
});