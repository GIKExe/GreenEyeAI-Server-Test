// document.addEventListener('DOMContentLoaded', () => {
//     if (!localStorage.getItem('auth_token')) {
//         window.location.href = '/admin/login';
//         return;
//     }
//     initAdmin();
// });

async function initAdmin() {
    loadAdminData();
    setupControls();
    setInterval(loadAdminData, 5000);
}

async function loadAdminData() {
    try {
        const state = await window.api.getLastState();
        const mode = await window.api.getMode();
        const schedule = await window.api.getSchedule();

        if (state) {
            document.getElementById('water-toggle').checked = !!state.water;
            document.getElementById('light-toggle').checked = !!state.light;
            document.getElementById('fan-toggle').checked = !!state.fan;
        }
        if (mode) {
            document.querySelector(`input[name="mode"][value="${mode.mode}"]`).checked = true;
        }
        if (schedule) {
            document.getElementById('light-start').value = schedule.light.start;
            document.getElementById('light-end').value = schedule.light.end;
            document.getElementById('water-interval').value = schedule.water.interval_hours;
            document.getElementById('water-duration').value = schedule.water.duration_minutes;
            document.getElementById('fan-interval').value = schedule.fan.interval_hours;
            document.getElementById('fan-duration').value = schedule.fan.duration_minutes;
        }
    } catch (e) {
        console.error(e);
    }
}

function setupControls() {
    // Тогглы устройств
    ['water', 'light', 'fan'].forEach(device => {
        const toggle = document.getElementById(`${device}-toggle`);
        toggle.addEventListener('change', async (e) => {
            try {
                await window.api.controlDevice(device, e.target.checked ? 'on' : 'off');
            } catch (err) {
                alert('Ошибка управления');
                e.target.checked = !e.target.checked; // Откат
            }
        });
    });

    // Переключение режима
    document.querySelectorAll('input[name="mode"]').forEach(radio => {
        radio.addEventListener('change', async (e) => {
            try {
                await window.api.setMode(e.target.value);
            } catch (err) {
                alert('Ошибка смены режима');
            }
        });
    });

    // Сохранение расписания
    document.getElementById('save-schedule').addEventListener('click', async () => {
        const schedule = {
            light: {
                start: document.getElementById('light-start').value,
                end: document.getElementById('light-end').value
            },
            water: {
                interval_hours: parseInt(document.getElementById('water-interval').value),
                duration_minutes: parseInt(document.getElementById('water-duration').value)
            },
            fan: {
                interval_hours: parseInt(document.getElementById('fan-interval').value),
                duration_minutes: parseInt(document.getElementById('fan-duration').value)
            }
        };
        try {
            await window.api.setSchedule(schedule);
            alert('Расписание сохранено!');
        } catch (err) {
            alert('Ошибка сохранения');
        }
    });

    // Выход
    document.getElementById('logout-btn').addEventListener('click', () => {
        window.api.logout();
    });
}