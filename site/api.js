class GreenEyeAPI {
    constructor() {
        this.token = localStorage.getItem('auth_token');
        this.baseUrl = ''; // Относительные пути, так как фронт и бэк на одном порту
    }

    async _fetch(endpoint, method = 'GET', body = null) {
        const options = { method, headers: {} };
        
        if (body && method !== 'GET') {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(body);
        }

        // Для GET запросов с параметрами (графики) формируем URL
        let url = this.baseUrl + endpoint;
        if (method === 'GET' && body) {
            const params = new URLSearchParams(body);
            url += (url.includes('?') ? '&' : '?') + params.toString();
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            // Если статус 204 или нет контента
            if (response.status === 204) return null;
            return await response.json();
        } catch (error) {
            console.error(`API Error: ${endpoint}`, error);
            throw error;
        }
    }

    // 🔐 Авторизация
    async login(username, password) {
        const data = await this._fetch('/api/admin/login', 'POST', { username, password });
        if (data && data.token) {
            this.token = data.token;
            localStorage.setItem('auth_token', this.token);
        }
        return data;
    }

    logout() {
        this.token = null;
        localStorage.removeItem('auth_token');
        window.location.href = '/';
    }

    //  Состояние (без токена, публично)
    async getLastState() {
        return this._fetch('/api/last_state', 'GET');
    }

    // 🎮 Управление устройствами (требует токена)
    async controlDevice(device, state) {
        if (!this.token) throw new Error('Not authorized');
        return this._fetch(`/api/command/${device}`, 'POST', { state, token: this.token });
    }

    // 🔄 Режим (Get без токена, Set с токеном)
    async getMode() {
        return this._fetch('/api/command/mode', 'GET');
    }

    async setMode(mode) {
        if (!this.token) throw new Error('Not authorized');
        return this._fetch('/api/command/mode', 'POST', { mode, token: this.token });
    }

    // 📅 Расписание (Get без токена, Set с токеном)
    async getSchedule() {
        return this._fetch('/api/schedule', 'GET');
    }

    async setSchedule(schedule) {
        if (!this.token) throw new Error('Not authorized');
        return this._fetch('/api/schedule', 'POST', { ...schedule, token: this.token });
    }

    // 📈 Графики (требует патча сервера для работы через GET params)
    async getGraphData(table, seconds = 86400) {
        return this._fetch('/api/graph/table', 'GET', { table, seconds });
    }
}

window.api = new GreenEyeAPI();