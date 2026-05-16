async function updateSchedule() {
	await fetch('/api/schedule')
		.then(res => res.json())
		.then(data => {
			const container = document.getElementById('schedule-view');
			container.innerHTML = '';
			const addCard = (icon, title, rows) => {
				const card = document.createElement('div');
				card.style.cssText = 'background: #f7fafc; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0;';
				let html = `<div style="font-weight: 600; margin-bottom: 10px; font-size: 16px;">${icon} ${title}</div>`;
				rows.forEach(([label, val]) => {
					html += `<div style="display: flex; justify-content: space-between; font-size: 14px; color: #4a5568; margin-bottom: 6px;">
							<span>${label}</span> <span style="font-weight: 500; color: #2d3748;">${val || '—'}</span>
						</div>`;
				});
				card.innerHTML = html;
				container.appendChild(card);
			};

			const l = data.light || data.osveshchenie || data.light_schedule;
			const f = data.fan || data.ventilyator || data.fan_schedule;
			const w = data.water || data.poliv || data.water_schedule;

			if (l) addCard('💡', 'Освещение', [['Включение', l.start || l.on || '—'], ['Выключение', l.end || l.off || '—']]);
			if (f) addCard('🌀', 'Обдув', [['Интервал', f.interval_hours ? `${f.interval_hours} ч` : '—'], ['Длительность', f.duration_minutes ? `${f.duration_minutes} мин` : '—']]);
			if (w) addCard('🚿', 'Полив', [['Интервал', w.interval_hours ? `${w.interval_hours} ч` : '—'], ['Длительность', w.duration_minutes ? `${w.duration_minutes} мин` : '—']]);

			if (!l && !f && !w) {
				const fallback = document.createElement('pre');
				fallback.style.cssText = 'background: #f7fafc; padding: 15px; border-radius: 12px; white-space: pre-wrap; font-family: monospace; font-size: 13px; color: #2d3748; grid-column: 1 / -1;';
				fallback.textContent = JSON.stringify(data, null, 2);
				container.appendChild(fallback);
			}
		})
		.catch(() => {
			document.getElementById('schedule-view').textContent = 'Ошибка загрузки расписания';
		});
}

async function updateState() {
	const rw = document.getElementById('relay-water');
	const rl = document.getElementById('relay-light');
	const rf = document.getElementById('relay-fan');
	const elements = [rw, rl, rf];
	await fetch('/api/last_state')
		.then(res => res.json())
		.then(data => {
			rw.textContent = (data.water ? 'ON' : 'OFF');
			rw.className = 'relay-status ' + (data.water ? 'on' : 'off');

			rl.textContent = (data.light ? 'ON' : 'OFF');
			rl.className = 'relay-status ' + (data.light ? 'on' : 'off');

			rf.textContent = (data.fan ? 'ON' : 'OFF');
			rf.className = 'relay-status ' + (data.fan ? 'on' : 'off');
		})
		.catch(() => {
			elements.forEach(element => {
				element.textContent = '???';
				element.className = 'relay-status wtf';
			});
		});
}

const activeCharts = {};

async function loadGraph(table, seconds) {
	const containerId = 'history-' + table;
	const container = document.getElementById(containerId);
	if (!container) return;

	// Находим canvas или создаём новый
	let canvas = container.querySelector('canvas');
	if (!canvas) {
		container.innerHTML = '';
		canvas = document.createElement('canvas');
		container.appendChild(canvas);
	}

	// Уничтожаем предыдущий график, если он существует
	if (activeCharts[containerId]) {
		activeCharts[containerId].destroy();
		delete activeCharts[containerId];
	}

	try {
		const res = await fetch('/api/graph/table', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ table, seconds })
		});
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const data = await res.json();

		if (!data || data.length === 0) {
			container.innerHTML = '<p style="text-align:center; color:gray;">Нет данных для отображения</p>';
			return;
		}

		const labels = data.map(([ts]) => {
			const d = new Date(ts * 1000);
			const hh = String(d.getHours()).padStart(2, '0');
			const mm = String(d.getMinutes()).padStart(2, '0');
			return `${hh}:${mm}`;
		});
		const states = data.map(([, state]) => state);

		activeCharts[containerId] = new Chart(canvas, {
			type: 'line',
			data: {
				labels,
				datasets: [{
					label: 'Состояние',
					data: states,
					borderColor: '#2563eb',
					backgroundColor: 'rgba(37, 99, 235, 0.15)',
					stepped: 'before',
					pointRadius: 3,
					pointHoverRadius: 6,
					fill: true
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				interaction: { mode: 'nearest', intersect: false },
				scales: {
					y: {
						min: -0.1, max: 1.1,
						ticks: { stepSize: 1, callback: v => v === 1 ? 'Вкл' : 'Выкл' },
						grid: { color: 'rgba(0,0,0,0.08)' }
					},
					x: { grid: { display: false }, ticks: { maxRotation: 45 } }
				},
				plugins: {
					legend: { display: false },
					tooltip: {
						callbacks: {
							title: items => `Время: ${items[0].label}`,
							label: ctx => `Состояние: ${ctx.raw === 1 ? 'Вкл' : 'Выкл'}`
						}
					}
				}
			}
		});
	} catch (err) {
		console.error(`Ошибка загрузки графика ${table}:`, err);
		container.innerHTML = '<p style="text-align:center; color:gray;">Ошибка загрузки данных</p>';
	}
}

async function updateGraphs() {
	const seconds = 21 * 24 * 60 * 60;
	await Promise.allSettled([
		loadGraph('water', seconds),
		loadGraph('light', seconds),
		loadGraph('fan', seconds)
	]);
}

async function updateAll() {
	await updateState();
	await updateSchedule();
	await updateGraphs();
}

updateAll();
setInterval(updateAll, 5000);