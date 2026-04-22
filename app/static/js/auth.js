// Хранение токена
let accessToken = null;

// Функция логина
async function login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch('/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
        credentials: 'include'
    });
    
    const data = await response.json();
    
    if (response.ok) {
        accessToken = data.access_token;
        // Сохраняем в localStorage
        localStorage.setItem('access_token', accessToken);
        return true;
    }
    return false;
}

// Функция получения заголовков с токеном
function authHeaders() {
    const token = accessToken || localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// Функция авторизованных запросов
async function authFetch(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...authHeaders(),
        ...options.headers
    };
    
    return fetch(url, {
        ...options,
        headers,
        credentials: 'include'
    });
}
