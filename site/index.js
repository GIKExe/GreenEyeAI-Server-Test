document.addEventListener('DOMContentLoaded', () => {
    initMonitoring();
});

async function initMonitoring() {
    updateDashboard();
    // Автообновление каждые 5 секунд
    setInterval(updateDashboard, 5000);
    // Графики обновляем реже (раз в минуту)
    setInterval(updateCharts, 60000);
    updateCharts();
}

async function updateDashboard() {
    try {
        const state = await window.api.getLastState();
        if (!state) return;

        // Обновляем индикаторы
        updateIndicator('water', state.water);
        updateIndicator('light', state.light);
        updateIndicator('fan', state.fan);
    } catch (e) {
        console.error('Update failed', e);
    }
}

function updateIndicator(device, isActive) {
    const el = document.getElementById(`${device}-status`);
    const badge = document.getElementById(`${device}-badge`);
    if (el) el.innerText = isActive ? 'Активно' : 'Неактивно';
    if (badge) {
        badge.className = isActive ? 'badge badge-success' : 'badge badge-danger';
        badge.innerText = isActive ? 'ON' : 'OFF';
    }
}

async function updateCharts() {
    try {
        // Загружаем данные за последние 24 часа
        const waterData = await window.api.getGraphData('water', 86400);
        if (waterData) drawSimpleChart('water-chart', waterData, 'Полив');
        
        const lightData = await window.api.getGraphData('light', 86400);
        if (lightData) drawSimpleChart('light-chart', lightData, 'Свет');
        
        const fanData = await window.api.getGraphData('fan', 86400);
        if (fanData) drawSimpleChart('fan-chart', fanData, 'Вентиляция');
    } catch (e) {
        console.error('Charts update failed', e);
    }
}

// Простая отрисовка графика на Canvas
function drawSimpleChart(canvasId, data, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width = canvas.offsetWidth;
    const h = canvas.height = 100;

    ctx.clearRect(0, 0, w, h);
    
    if (!data || data.length === 0) {
        ctx.fillStyle = '#8fa888';
        ctx.fillText('Нет данных', w/2 - 20, h/2);
        return;
    }

    // Рисуем линию состояния (0 или 1)
    ctx.beginPath();
    ctx.strokeStyle = '#7fc950';
    ctx.lineWidth = 2;

    const now = Date.now() / 1000;
    const startTime = now - 86400;
    
    // Находим мин/макс время для масштабирования
    const minT = data[0].timestamp;
    const maxT = data[data.length - 1].timestamp;
    const range = maxT - minT || 1;

    data.forEach((point, i) => {
        const x = ((point.timestamp - minT) / range) * w;
        const y = point.state ? 10 : 90; // 1 - вверху, 0 - внизу
        
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Подпись
    ctx.fillStyle = '#1e2420';
    ctx.font = '12px Inter';
    ctx.fillText(label, 10, 20);
}