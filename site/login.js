document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    const err = document.getElementById('login-error');

    try {
        await window.api.login(u, p);
        window.location.href = '/admin';
    } catch (e) {
        err.style.display = 'block';
        err.innerText = 'Неверный логин или пароль';
    }
});