/* ============================================================
   Financial Analytics Platform - Application Logic
   ============================================================ */

const API_BASE = '';
let messageTimeout;

const state = {
    token: null,
    metrics: [],
    currentDatatype: '',
    currentMetric: null,
    lastResult: null,
    chartInstance: null,
    portfolioChartInstance: null,
    portfolioHoldings: [],
    portfolioSecuritiesLoaded: false,
    sort: { column: null, direction: 1 }
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('loginBtn').addEventListener('click', handleLogin);
    document.getElementById('datatype').addEventListener('change', handleDatatypeChange);
    document.getElementById('metric').addEventListener('change', handleMetricChange);
    document.getElementById('executeBtn').addEventListener('click', handleExecute);
    document.getElementById('resetBtn').addEventListener('click', handleReset);
    document.getElementById('exportCsvBtn').addEventListener('click', handleExportCsv);
    document.getElementById('metricsNavBtn').addEventListener('click', () => setActiveDashboardPage('metrics'));
    document.getElementById('qualityNavBtn').addEventListener('click', () => setActiveDashboardPage('quality'));
    document.getElementById('portfolioNavBtn').addEventListener('click', () => setActiveDashboardPage('portfolio'));
    document.getElementById('addPortfolioHoldingBtn').addEventListener('click', handleAddPortfolioHolding);
    document.getElementById('runPortfolioSimulationBtn').addEventListener('click', handleRunPortfolioSimulation);
    document.getElementById('qualityDatatype').addEventListener('change', handleQualityDatatypeChange);
    document.getElementById('runQualityChecksBtn').addEventListener('click', handleRunQualityChecks);

    // Read-only metric info panel; runs after the existing handlers' synchronous work.
    document.getElementById('metric').addEventListener('change', updateMetricInfo);
    document.getElementById('datatype').addEventListener('change', updateMetricInfo);
    document.getElementById('resetBtn').addEventListener('click', updateMetricInfo);
});

/* ================= DATA QUALITY CENTER ================= */

function setActiveDashboardPage(page) {
    const metricsActive = page === 'metrics';
    const qualityActive = page === 'quality';
    const portfolioActive = page === 'portfolio';
    document.getElementById('metricsPage').style.display = metricsActive ? 'flex' : 'none';
    document.getElementById('qualityPage').style.display = qualityActive ? 'flex' : 'none';
    document.getElementById('portfolioPage').style.display = portfolioActive ? 'flex' : 'none';
    document.getElementById('metricsNavBtn').setAttribute(
        'aria-current',
        metricsActive ? 'page' : 'false'
    );
    document.getElementById('qualityNavBtn').setAttribute(
        'aria-current',
        qualityActive ? 'page' : 'false'
    );
    document.getElementById('portfolioNavBtn').setAttribute(
        'aria-current',
        portfolioActive ? 'page' : 'false'
    );

    if (portfolioActive && !state.portfolioSecuritiesLoaded) {
        loadPortfolioSecurities();
    }
}

/* ================= PORTFOLIO RISK SIMULATOR ================= */

const portfolioTickerColors = new Map();
const portfolioPalette = [
    '#1d4ed8', '#0284c7', '#6366f1', '#d97706',
    '#16a34a', '#dc2626', '#7c3aed', '#0891b2'
];

function getPortfolioTickerColor(ticker) {
    if (!portfolioTickerColors.has(ticker)) {
        portfolioTickerColors.set(
            ticker,
            portfolioPalette[portfolioTickerColors.size % portfolioPalette.length]
        );
    }
    return portfolioTickerColors.get(ticker);
}

function renderPortfolioInterpretation() {
    const riskElement = document.getElementById('portfolioRiskScore');
    const risk = riskElement.textContent.toLowerCase();
    const volatility = document.getElementById('portfolioVolatility').textContent;
    const count = document.querySelector('[data-portfolio-holdings-count]').textContent;
    const largest = document.querySelector('[data-portfolio-largest-position]').textContent;
    const total = document.querySelector('[data-portfolio-total-allocation]').textContent;
    const text = `This is a ${risk}-risk portfolio with estimated volatility of ${volatility}. ` +
        `The portfolio contains ${count} holdings. The largest position is ${largest}. ` +
        `Total allocation is ${total}.`;

    riskElement.dataset.risk = risk;
    riskElement.setAttribute('aria-label', `${riskElement.textContent} Risk`);
    document.querySelectorAll('[data-portfolio-interpretation]').forEach(element => {
        element.textContent = text;
    });
}

async function loadPortfolioSecurities() {
    const securitySelect = document.getElementById('portfolioSecuritySelect');

    try {
        const response = await fetch(`${API_BASE}/api/portfolio/securities`, {
            headers: authHeaders()
        });
        const data = await response.json();
        if (!response.ok || data.status !== 'ok' || !Array.isArray(data.securities)) {
            throw new Error(data.message || 'Failed to load portfolio securities');
        }

        securitySelect.replaceChildren(new Option('-- Select Security --', ''));
        data.securities.forEach(ticker => {
            securitySelect.add(new Option(ticker, ticker));
        });
        state.portfolioSecuritiesLoaded = true;
        setPortfolioMessage(
            data.securities.length ? '' : 'No securities are available in the STOCK dataset.',
            data.securities.length ? '' : 'info'
        );
    } catch (error) {
        setPortfolioMessage(error.message || 'Failed to load portfolio securities', 'error');
    }
}

function handleAddPortfolioHolding() {
    const ticker = document.getElementById('portfolioSecuritySelect').value;
    const weight = Number(document.getElementById('portfolioWeightInput').value);

    if (!ticker) {
        setPortfolioMessage('Please select a security.', 'error');
        return;
    }
    if (!Number.isFinite(weight) || weight <= 0 || weight > 100) {
        setPortfolioMessage('Enter an allocation greater than 0% and at most 100%.', 'error');
        return;
    }
    if (state.portfolioHoldings.some(holding => holding.ticker === ticker)) {
        setPortfolioMessage(`${ticker} is already in the portfolio.`, 'error');
        return;
    }

    state.portfolioHoldings.push({ ticker, weight });
    document.getElementById('portfolioWeightInput').value = '';
    setPortfolioMessage('');
    renderPortfolioHoldings();
}

function renderPortfolioHoldings() {
    const body = document.getElementById('portfolioHoldingsBody');
    body.replaceChildren();
    let largestHolding = null;

    state.portfolioHoldings.forEach((holding, index) => {
        const row = document.createElement('tr');
        const tickerCell = document.createElement('td');
        const securityBadge = document.createElement('span');
        securityBadge.className = 'portfolio-security-badge';
        securityBadge.textContent = holding.ticker;
        tickerCell.appendChild(securityBadge);
        const weightCell = document.createElement('td');
        const weightBadge = document.createElement('span');
        weightBadge.className = 'portfolio-allocation-badge';
        weightBadge.textContent = `${holding.weight.toFixed(2)}%`;
        weightCell.appendChild(weightBadge);
        const actionCell = document.createElement('td');
        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'portfolio-remove-button';
        removeButton.textContent = 'Remove';
        removeButton.setAttribute('aria-label', `Remove ${holding.ticker}`);
        removeButton.addEventListener('click', () => {
            state.portfolioHoldings.splice(index, 1);
            setPortfolioMessage('');
            renderPortfolioHoldings();
        });
        actionCell.appendChild(removeButton);
        row.append(tickerCell, weightCell, actionCell);
        body.appendChild(row);
        if (!largestHolding || holding.weight > largestHolding.weight) {
            largestHolding = holding;
        }
    });

    const total = state.portfolioHoldings.reduce((sum, holding) => sum + holding.weight, 0);
    const allocationValid = Math.abs(total - 100) <= 1e-6;
    document.getElementById('portfolioTotalAllocation').textContent = `${total.toFixed(2)}%`;
    document.querySelector('[data-portfolio-holdings-count]').textContent =
        String(state.portfolioHoldings.length);
    document.querySelector('[data-portfolio-largest-position]').textContent =
        largestHolding ? `${largestHolding.ticker} (${largestHolding.weight.toFixed(2)}%)` : '--';
    document.querySelector('[data-portfolio-total-allocation]').textContent =
        document.getElementById('portfolioTotalAllocation').textContent;
    document.getElementById('portfolioAllocationWarning').hidden = allocationValid;
    document.getElementById('runPortfolioSimulationBtn').disabled =
        !allocationValid || state.portfolioHoldings.length === 0;
    clearPortfolioResults();
}

async function handleRunPortfolioSimulation() {
    const button = document.getElementById('runPortfolioSimulationBtn');
    if (button.disabled) {
        return;
    }

    button.disabled = true;
    button.textContent = 'Running...';
    clearPortfolioResults();
    setPortfolioMessage('Running portfolio simulation...', 'info');

    try {
        const response = await fetch(`${API_BASE}/api/portfolio/simulate`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({ holdings: state.portfolioHoldings })
        });
        const data = await response.json();
        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.message || 'Portfolio simulation failed');
        }

        document.getElementById('portfolioExpectedReturn').textContent =
            `${Number(data.expected_return).toFixed(2)}%`;
        document.getElementById('portfolioVolatility').textContent =
            `${Number(data.volatility).toFixed(2)}%`;
        document.getElementById('portfolioRiskScore').textContent = data.risk_score;
        renderPortfolioInterpretation();
        document.getElementById('portfolioChartPlaceholder').hidden = true;
        document.getElementById('portfolioResults').hidden = false;
        renderPortfolioChart(data.chart);
        updateLastRefresh();
        setPortfolioMessage('');
    } catch (error) {
        setPortfolioMessage(error.message || 'Portfolio simulation failed', 'error');
    } finally {
        button.textContent = 'Run Simulation';
        button.disabled = Math.abs(
            state.portfolioHoldings.reduce((sum, holding) => sum + holding.weight, 0) - 100
        ) > 1e-6 || state.portfolioHoldings.length === 0;
    }
}

function renderPortfolioChart(chart) {
    if (state.portfolioChartInstance) {
        state.portfolioChartInstance.destroy();
        state.portfolioChartInstance = null;
    }

    const canvas = document.getElementById('portfolioAllocationChart');
    state.portfolioChartInstance = new Chart(canvas, {
        type: 'pie',
        data: {
            labels: chart.labels,
            datasets: [{
                data: chart.values,
                backgroundColor: chart.labels.map(getPortfolioTickerColor),
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label(context) {
                            return `${context.label}: ${Number(context.raw).toFixed(2)}%`;
                        }
                    }
                }
            }
        }
    });
}

function clearPortfolioResults() {
    document.getElementById('portfolioResults').hidden = true;
    document.getElementById('portfolioChartPlaceholder').hidden = false;
    document.querySelectorAll('[data-portfolio-interpretation]').forEach(element => {
        element.textContent = 'Run a simulation to view a rules-based interpretation of the portfolio results.';
    });
    if (state.portfolioChartInstance) {
        state.portfolioChartInstance.destroy();
        state.portfolioChartInstance = null;
    }
}

function setPortfolioMessage(message, type = '') {
    const element = document.getElementById('portfolioStatusMessage');
    element.textContent = message;
    element.className = `portfolio-status-message${type ? ` ${type}` : ''}`;
}

function handleQualityDatatypeChange(event) {
    document.getElementById('runQualityChecksBtn').disabled = !event.target.value;
    document.getElementById('qualityResultsSection').hidden = true;
    document.getElementById('qualityCheckList').replaceChildren();
    setQualityMessage('');
}

async function handleRunQualityChecks() {
    const datatype = document.getElementById('qualityDatatype').value;
    if (!datatype) {
        setQualityMessage('Please select a dataset.', 'error');
        return;
    }

    const button = document.getElementById('runQualityChecksBtn');
    const resultsSection = document.getElementById('qualityResultsSection');
    button.disabled = true;
    button.textContent = 'Running...';
    resultsSection.hidden = false;
    document.getElementById('qualityCheckList').replaceChildren();
    setQualityMessage('Running quality checks...', 'info');

    try {
        const response = await fetch(
            `${API_BASE}/api/quality?datatype=${encodeURIComponent(datatype)}`,
            { headers: authHeaders() }
        );
        const data = await response.json();

        if (!response.ok || data.status !== 'ok') {
            throw new Error(data.message || 'Failed to run quality checks');
        }
        if (!Array.isArray(data.checks)) {
            throw new Error('The quality-check response was invalid.');
        }

        renderQualityChecks(datatype, data.checks);
        updateLastRefresh();
        setQualityMessage(`Completed ${data.checks.length} quality checks.`, 'success');
    } catch (err) {
        resultsSection.hidden = true;
        setQualityMessage(err.message || 'Failed to run quality checks', 'error');
    } finally {
        button.disabled = !document.getElementById('qualityDatatype').value;
        button.textContent = 'Run Checks';
    }
}

function renderQualityChecks(datatype, checks) {
    const datasetName = document.getElementById('qualityDatatype').selectedOptions[0].textContent;
    document.getElementById('qualityResultsTitle').textContent =
        `${datasetName} Quality Check Results`;
    document.getElementById('qualityResultsDescription').textContent =
        `${checks.length} checks completed for ${datasetName}. Select a check to view details.`;

    const checkList = document.getElementById('qualityCheckList');
    checkList.replaceChildren();

    checks.forEach(check => {
        const card = document.createElement('article');
        card.className = 'quality-check-card';

        const toggle = document.createElement('button');
        toggle.className = 'quality-check-toggle';
        toggle.type = 'button';
        toggle.setAttribute('aria-expanded', 'false');

        const name = document.createElement('span');
        name.className = 'quality-check-name';
        name.textContent = check.check_name;

        const status = document.createElement('span');
        status.className = `quality-check-status ${check.status === 'PASS' ? 'pass' : 'fail'}`;
        status.textContent = check.status;

        const count = document.createElement('span');
        count.className = 'quality-check-count';
        count.textContent = `${check.offending_count} offending ${check.offending_count === 1 ? 'row' : 'rows'}`;

        toggle.append(name, status, count);

        const details = document.createElement('div');
        details.className = 'quality-check-details';
        details.hidden = true;
        if (check.status === 'PASS') {
            const message = document.createElement('p');
            message.className = 'quality-pass-message';
            message.textContent = 'No offending rows detected.';
            details.appendChild(message);
        } else if (Array.isArray(check.sample_rows) && check.sample_rows.length) {
            details.appendChild(createQualitySampleTable(check.sample_rows));
        } else {
            const message = document.createElement('p');
            message.className = 'quality-empty-sample';
            message.textContent = 'This check failed, but no sample rows were provided.';
            details.appendChild(message);
        }

        toggle.addEventListener('click', () => {
            const expanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', String(!expanded));
            details.hidden = expanded;
        });

        card.append(toggle, details);
        checkList.appendChild(card);
    });
}

function createQualitySampleTable(rows) {
    const wrapper = document.createElement('div');
    wrapper.className = 'quality-sample-scroll';
    const table = document.createElement('table');
    table.className = 'quality-sample-table';
    const columns = [...new Set(rows.flatMap(row => Object.keys(row)))];
    const head = document.createElement('thead');
    const headerRow = document.createElement('tr');
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
    });
    head.appendChild(headerRow);

    const body = document.createElement('tbody');
    rows.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(column => {
            const td = document.createElement('td');
            const value = row[column];
            td.textContent = value === null || value === undefined ? '' : String(value);
            tr.appendChild(td);
        });
        body.appendChild(tr);
    });

    table.append(head, body);
    wrapper.appendChild(table);
    return wrapper;
}

function setQualityMessage(message, type) {
    const element = document.getElementById('qualityStatusMessage');
    element.textContent = message;
    element.className = `quality-status-message${message ? ` ${type || 'info'}` : ''}`;
}

/* ================= METRIC INFORMATION (READ-ONLY) ================= */

function updateMetricInfo() {
    const section = document.getElementById('metricInfoSection');
    const metricId = document.getElementById('metric').value;
    const tip = metricId
        ? Array.from(document.querySelectorAll('.metric-tip')).find(el => el.dataset.metric === metricId)
        : null;

    if (!tip) {
        section.style.display = 'none';
        return;
    }

    const title = tip.querySelector('.tooltip-title');
    const formula = tip.querySelector('.tooltip-formula');
    const definition = tip.querySelector('.tooltip-definition');

    document.getElementById('metricInfoName').textContent = title ? title.textContent : '';

    const formulaTarget = document.getElementById('metricInfoFormula');
    formulaTarget.replaceChildren(...(formula ? Array.from(formula.childNodes, node => node.cloneNode(true)) : []));
    document.getElementById('metricInfoFormulaRow').style.display = formula ? '' : 'none';

    document.getElementById('metricInfoDefinition').textContent = definition ? definition.textContent : '';
    document.getElementById('metricInfoInterpretation').textContent = tip.dataset.interpretation || '';

    section.style.display = 'block';
}

/* ================= STATUS / MESSAGE HELPERS ================= */

function showMessage(text, type) {
    const el = document.getElementById('statusMessage');
    clearTimeout(messageTimeout);
    el.textContent = text;
    el.className = 'status-message visible ' + (type || 'info');
    if (type === 'success') {
        messageTimeout = setTimeout(() => {
            el.classList.add('fading-out');
            messageTimeout = setTimeout(clearMessage, 400);
        }, 3000);
    }
}

function clearMessage() {
    clearTimeout(messageTimeout);
    messageTimeout = null;
    const el = document.getElementById('statusMessage');
    el.textContent = '';
    el.className = 'status-message';
}

function setConnectionStatus(connected) {
    const dot = document.getElementById('connectionDot');
    const text = document.getElementById('connectionText');
    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Authenticated';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Not authenticated';
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
        setMetricInitialState(false);
        clearMessage();
    } catch (err) {
        clearMetricOutput();
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

    clearMetricOutput();
}

function setMetricInitialState(visible) {
    document.getElementById('visualizationInitialState').hidden = !visible;
    document.getElementById('resultsInitialState').hidden = !visible;
}

function clearMetricOutput() {
    state.lastResult = null;
    state.sort = { column: null, direction: 1 };

    document.getElementById('tableSection').style.display = 'none';
    document.getElementById('chartSection').style.display = 'none';
    document.getElementById('tableHead').innerHTML = '';
    document.getElementById('tableBody').innerHTML = '';

    if (state.chartInstance) {
        state.chartInstance.destroy();
        state.chartInstance = null;
    }

    setMetricInitialState(true);
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
const METRIC_CHART_PALETTE = [
    '#1D4ED8', '#0284C7', '#6366F1', '#D97706',
    '#16A34A', '#DC2626', '#7C3AED', '#0891B2'
];

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
    const selectedDatatype = document.getElementById('datatype').selectedOptions[0];
    chartSection.querySelector('[data-context-dataset]').textContent =
        selectedDatatype ? selectedDatatype.textContent : '—';
    chartSection.querySelector('[data-context-metric]').textContent =
        state.currentMetric ? state.currentMetric.name : '—';
    chartSection.querySelector('[data-context-records]').textContent =
        state.lastResult && state.lastResult.rows ? state.lastResult.rows.length : '—';

    if (state.chartInstance) {
        state.chartInstance.destroy();
        state.chartInstance = null;
    }

    const hasDatasets = chart && Array.isArray(chart.datasets) && chart.datasets.length > 0;
    const hasValues = chart && Array.isArray(chart.values) && chart.values.length > 0;

    if (
        !chart ||
        !Array.isArray(chart.labels) ||
        !chart.labels.length ||
        (!hasDatasets && !hasValues)
    ) {
        canvas.style.display = 'none';
        chartEmpty.style.display = 'block';
        return;
    }

    canvas.style.display = 'block';
    chartEmpty.style.display = 'none';

    const chartType = resolveChartType(state.currentMetric);
    const label = state.currentMetric ? state.currentMetric.name : 'Value';

    let data;
    if (hasDatasets) {
        data = {
            labels: chart.labels,
            datasets: chart.datasets.map((dataset, index) => {
                const color = METRIC_CHART_PALETTE[index % METRIC_CHART_PALETTE.length];
                return {
                    ...dataset,
                    backgroundColor: color,
                    borderColor: color,
                    borderWidth: 1.5,
                    fill: false,
                    spanGaps: false,
                    tension: 0.2,
                    pointRadius: 2
                };
            })
        };
    } else if (chartType === 'scatter') {
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
                spanGaps: false,
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
