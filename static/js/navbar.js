document.addEventListener('DOMContentLoaded', () => {
    const access = localStorage.getItem('access');
    const user = JSON.parse(localStorage.getItem('user'));

    const navLogin = document.getElementById('nav-login');
    const navRegister = document.getElementById('nav-register');
    const userNav = document.getElementById('user-nav');
    const userName = document.getElementById('user-name-display');
    const logoutLink = document.getElementById('logoutlink');

    if (access && user) {
        userNav?.classList.remove('d-none');
        navLogin?.classList.add('d-none');
        navRegister?.classList.add('d-none');
        if (userName) userName.textContent = user.name || user.email;
    } else {
        userNav?.classList.add('d-none');
        navLogin?.classList.remove('d-none');
        navRegister?.classList.remove('d-none');
    }

    logoutLink?.addEventListener('click', async (e) => {
        e.preventDefault();
        const refresh = localStorage.getItem('refresh');

        try {
            await fetch('/api/auth/logout/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh }),
            });
        } catch (error) {
            console.warn('Logout failed:', error);
        }

        localStorage.clear();
        window.location.href = '/';
    });
});
