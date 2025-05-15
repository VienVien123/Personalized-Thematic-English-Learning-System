document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('change-password-form');
    if (!form) return;

    const token = localStorage.getItem('access');
    if (!token) {
        alert('Bạn cần đăng nhập để đổi mật khẩu!');
        window.location.href = '/login/';
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const old_password = document.getElementById('old-password').value;
        const new_password = document.getElementById('new-password').value;
        const confirm_password = document.getElementById('confirm-password').value;

        const response = await fetch('/api/user/change-password/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ old_password, new_password, confirm_password })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Đổi mật khẩu thành công!");
            window.location.href = '/';
        } else {
            const firstKey = Object.keys(data)[0];
            alert(data[firstKey][0]);
        }
    });
});
