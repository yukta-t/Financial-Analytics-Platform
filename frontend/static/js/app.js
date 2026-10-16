/* ============================================================
   Financial Analytics Platform - Application Logic
   ============================================================ */

const API_BASE = '';

const state = {
    token: null,
    metrics: [],
    currentDatatype: '',
    currentMetric: null,
    lastResult: null,
    chartInstance: null,
    sort: { column: null, direction: 1 }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('loginBtn').addEventListener('click', handleLogin);
    document.getElementById('datatype').addEventListener('change', handleDatatypeChange);
    document.getElementById('metric').addEventListener('change', handleMetricChange);
    document.getElementById('executeBtn').addEventListener('click', handleExecute);
    document.getElementById('resetBtn').addEventListener('click', handleReset);
    document.getElementById('exportCsvBtn').addEventListener('click', handleExportCsv);
});

/* ================= STATUS / MESSAGE HELPERS ================= */

function showMessage(text, type) {
    const el = document.getElementById('statusMessage');
    el.textContent = text;
    el.className = 'status-message visible ' + (type || 'info');
}

function clearMessage() {
    const el = document.getElementById('statusMessage');
    el.textContent = '';
    el.className = 'status-message';
}

function setConnectionStatus(connected) {
    const dot = document.getElementById('connectionDot');
    const text = document.getElementById('connectionText');
    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

function updateLastRefresh() {
    const now = new Date();
    document.getElementById('lastRefreshTime').textContent = now.toLocaleTimeString();
}

/* ================= LOGIN ================= */

async function handleLogin() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showMessage('Username and password are required.', 'error');
        return;
    }

    clearMessage();
    const loginBtn = document.getElementById('loginBtn');
    loginBtn.disabled = true;
    loginBtn.textContent = 'Signing in...';

    try {
        const response = await fetch(`${API_BASE}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.message || 'Login failed');
        }

        state.token = data.access_token;
        setConnectionStatus(true);
        updateLastRefresh();
        document.getElementById('loginBar').style.display = 'none';
        document.getElementById('appMain').style.display = 'flex';
        showMessage('Login successful.', 'success');
    } catch (err) {
        setConnectionStatus(false);
        showMessage(err.message || 'Login failed', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = 'Login';
    }
}

function authHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.token}`
    };
}

/* ================= DATA TYPE / METRIC ================= */

async function handleDatatypeChange(event) {
    const datatype = event.target.value;
    state.currentDatatype = datatype;
    state.metrics = [];
    state.currentMetric = null;

    const metricSelect = document.getElementById('metric');
    metricSelect.innerHTML = '<option value="">-- Select --</option>';
    metricSelect.disabled = true;
    document.getElementById('paramField').style.display = 'none';
    document.getElementById('executeBtn').disabled = true;

    if (!datatype) {
        return;
    }

    clearMessage();

    try {
        const response = await fetch(`${API_BASE}/api/metrics?datatype=${encodeURIComponent(datatype)}`, {
            headers: authHeaders()
        });

        const data = await response.json();

        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.message || 'Failed to load metrics');
        }

        state.metrics = data.metrics || [];
        updateLastRefresh();

        state.metrics.forEach(metric => {
            const option = document.createElement('option');
            option.value = metric.id;
            option.textContent = metric.name;
            metricSelect.appendChild(option);
        });

        metricSelect.disabled = false;
    } catch (err) {
        showMessage(err.message || 'Failed to load metrics', 'error');
    }
}

function handleMetricChange(event) {
    const metricId = event.target.value;
    state.currentMetric = state.metrics.find(m => m.id === metricId) || null;

    const needsWindow = metricRequiresWindowParam(state.currentMetric);
    document.getElementById('paramField').style.display = needsWindow ? 'flex' : 'none';

    document.getElementById('executeBtn').disabled = !metricId;
}

function metricRequiresWindowParam(metric) {
    if (!metric) return false;
    const key = `${metric.id} ${metric.name}`.toLowerCase();
    return (
        key.includes('sma') ||
        key.includes('ema') ||
        key.includes('moving average') ||
        key.includes('exponential') ||
        key.includes('volatility')
    );
}

/* ================= EXECUTE ================= */

async function handleExecute() {
    if (!state.currentDatatype || !state.currentMetric) {
        showMessage('Please select a Data Type and Metric.', 'error');
        return;
    }

    const params = {};
    if (metricRequiresWindowParam(state.currentMetric)) {
        params.window = Number(document.getElementById('windowSize').value) || 20;
    }

    const executeBtn = document.getElementById('executeBtn');
    executeBtn.disabled = true;
    executeBtn.textContent = 'Executing...';
    clearMessage();
    showMessage('Executing metric query...', 'info');

    try {
        const response = await fetch(`${API_BASE}/api/execute`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                datatype: state.currentDatatype,
                metric_id: state.currentMetric.id,
                params
            })
        });

        const data = await response.json();

        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.message || 'Execution failed');
        }

        state.lastResult = data;
        state.sort = { column: null, direction: 1 };
        updateLastRefresh();
        renderTable(data.columns || [], data.rows || []);
        renderChart(data.chart);
        clearMessage();
    } catch (err) {
        showMessage(err.message || 'Execution failed', 'error');
    } finally {
        executeBtn.disabled = false;
        executeBtn.textContent = 'Execute';
    }
}

/* ================= RESET ================= */

function handleReset() {
    document.getElementById('datatype').value = '';
    document.getElementById('metric').innerHTML = '<option value="">-- Select --</option>';
    document.getElementById('metric').disabled = true;
    document.getElementById('paramField').style.display = 'none';
    document.getElementById('windowSize').value = 20;
    document.getElementById('executeBtn').disabled = true;

    state.currentDatatype = '';
    state.currentMetric = null;
    state.metrics = [];
    state.lastResult = null;
    state.sort = { column: null, direction: 1 };

    clearMessage();

    document.getElementById('tableSection').style.display = 'none';
    document.getElementById('chartSection').style.display = 'none';
    document.getElementById('tableHead').innerHTML = '';
    document.getElementById('tableBody').innerHTML = '';

    if (state.chartInstance) {
        state.chartInstance.destroy();
        state.chartInstance = null;
    }
}

/* ================= TABLE ================= */

function renderTable(columns, rows) {
    const tableSection = document.getElementById('tableSection');
    const head = document.getElementById('tableHead');
    const body = document.getElementById('tableBody');

    head.innerHTML = '';
    body.innerHTML = '';

    if (!columns.length) {
        tableSection.style.display = 'none';
        return;
    }

    columns.forEach((col, index) => {
        const th = document.createElement('th');
        th.textContent = col;
        th.dataset.index = index;
        const arrow = document.createElement('span');
        arrow.className = 'sort-arrow';
        th.appendChild(arrow);
        th.addEventListener('click', () => handleSort(index));
        head.appendChild(th);
    });

    renderRows(rows);
    document.getElementById('recordCount').textContent = `${rows.length} records`;
    tableSection.style.display = 'block';
}

function renderRows(rows) {
    const body = document.getElementById('tableBody');
    body.innerHTML = '';

    rows.forEach(row => {
        const tr = document.createElement('tr');
        row.forEach(value => {
            const td = document.createElement('td');
            td.textContent = value === null || value === undefined ? '' : value;
            tr.appendChild(td);
        });
        body.appendChild(tr);
    });
}

function handleSort(columnIndex) {
    if (!state.lastResult) return;

    if (state.sort.column === columnIndex) {
        state.sort.direction *= -1;
    } else {
        state.sort.column = columnIndex;
        state.sort.direction = 1;
    }

    const rows = [...state.lastResult.rows];
    rows.sort((a, b) => {
        const valA = a[columnIndex];
        const valB = b[columnIndex];
        const numA = Number(valA);
        const numB = Number(valB);
        let comparison;
        if (!Number.isNaN(numA) && !Number.isNaN(numB) && valA !== '' && valB !== '') {
            comparison = numA - numB;
        } else {
            comparison = String(valA).localeCompare(String(valB));
        }
        return comparison * state.sort.direction;
    });

    renderRows(rows);

    const headers = document.querySelectorAll('#tableHead th');
    headers.forEach((th, index) => {
        const arrow = th.querySelector('.sort-arrow');
        if (index === columnIndex) {
            arrow.textContent = state.sort.direction === 1 ? '▲' : '▼';
        } else {
            arrow.textContent = '';
        }
    });
}

/* ================= EXPORT CSV ================= */

function handleExportCsv() {
    if (!state.lastResult || !state.lastResult.columns || !state.lastResult.columns.length) {
        showMessage('No results available to export.', 'error');
        return;
    }

    const { columns, rows } = state.lastResult;
    const csvLines = [columns.join(',')];

    rows.forEach(row => {
        const line = row.map(value => {
            const str = value === null || value === undefined ? '' : String(value);
            if (str.includes(',') || str.includes('"') || str.includes('\n')) {
                return `"${str.replace(/"/g, '""')}"`;
            }
            return str;
        }).join(',');
        csvLines.push(line);
    });

    const blob = new Blob([csvLines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${state.currentDatatype}_${state.currentMetric ? state.currentMetric.id : 'result'}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/* ================= CHART ================= */

const LINE_CHART_METRICS = ['daily_return', 'log_return', 'sma', 'ema', 'volatility', 'dividend_yield'];
const BAR_CHART_METRICS = ['currency_distribution', 'related_securities_count'];
const SCATTER_CHART_METRICS = ['price_vs_duration', 'price_duration'];

function resolveChartType(metric) {
    if (!metric) return 'line';
    const key = `${metric.id} ${metric.name}`.toLowerCase();

    if (SCATTER_CHART_METRICS.some(k => key.includes(k)) || (key.includes('price') && key.includes('duration'))) {
        return 'scatter';
    }
    if (BAR_CHART_METRICS.some(k => key.includes(k)) || key.includes('distribution') || key.includes('count')) {
        return 'bar';
    }
    if (LINE_CHART_METRICS.some(k => key.includes(k))) {
        return 'line';
    }
    return 'line';
}

function renderChart(chart) {
    const chartSection = document.getElementById('chartSection');
    const chartEmpty = document.getElementById('chartEmpty');
    const canvas = document.getElementById('metricChart');

    chartSection.style.display = 'block';

    if (state.chartInstance) {
        state.chartInstance.destroy();
        state.chartInstance = null;
    }

    if (!chart || !chart.labels || !chart.labels.length || !chart.values || !chart.values.length) {
        canvas.style.display = 'none';
        chartEmpty.style.display = 'block';
        return;
    }

    canvas.style.display = 'block';
    chartEmpty.style.display = 'none';

    const chartType = resolveChartType(state.currentMetric);
    const label = state.currentMetric ? state.currentMetric.name : 'Value';

    let data;
    if (chartType === 'scatter') {
        data = {
            datasets: [{
                label,
                data: chart.labels.map((x, i) => ({ x: Number(x), y: Number(chart.values[i]) })),
                backgroundColor: '#115ea3'
            }]
        };
    } else {
        data = {
            labels: chart.labels,
            datasets: [{
                label,
                data: chart.values,
                backgroundColor: chartType === 'bar' ? '#115ea3' : 'rgba(17, 94, 163, 0.1)',
                borderColor: '#115ea3',
                borderWidth: 1.5,
                fill: chartType === 'line',
                tension: 0.2,
                pointRadius: chartType === 'line' ? 2 : 0
            }]
        };
    }

    state.chartInstance = new Chart(canvas, {
        type: chartType,
        data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true }
            },
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: '#e1dfdd' } }
            }
        }
    });
}
