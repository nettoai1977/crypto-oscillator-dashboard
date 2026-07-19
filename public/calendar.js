/* Crypto Calendar — Monthly Performance Heatmap + Seasonality */

const CAL_COINS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'];
const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

async function fetchMonthlyKlines(symbol, limit = 36) {
    try {
        const r = await fetch(`${BINANCE_API}/klines?symbol=${symbol}&interval=1M&limit=${limit}`);
        const data = await r.json();
        return data.map(k => ({
            open: parseFloat(k[1]),
            close: parseFloat(k[4]),
            high: parseFloat(k[2]),
            low: parseFloat(k[3]),
            time: k[0],
            date: new Date(k[0])
        }));
    } catch (e) {
        console.error(`Failed to fetch monthly ${symbol}:`, e);
        return [];
    }
}

function calcMonthlyReturns(klines) {
    return klines.map(k => {
        const ret = ((k.close - k.open) / k.open) * 100;
        const vol = ((k.high - k.low) / k.open) * 100;
        return {
            year: k.date.getFullYear(),
            month: k.date.getMonth(),
            return: ret,
            volatility: vol,
            open: k.open,
            close: k.close
        };
    });
}

function calcSeasonality(monthlyReturns) {
    const byMonth = {};
    for (let i = 0; i < 12; i++) byMonth[i] = [];
    monthlyReturns.forEach(r => byMonth[r.month].push(r.return));

    const result = [];
    for (let i = 0; i < 12; i++) {
        const rets = byMonth[i];
        const avg = rets.length ? rets.reduce((a, b) => a + b, 0) / rets.length : 0;
        const greenPct = rets.length ? (rets.filter(r => r > 0).length / rets.length * 100) : 0;
        result.push({ month: i, avg, greenPct, count: rets.length });
    }
    return result;
}

function calcQuarterly(monthlyReturns) {
    const quarters = { Q1: [], Q2: [], Q3: [], Q4: [] };
    monthlyReturns.forEach(r => {
        if (r.month < 3) quarters.Q1.push(r.return);
        else if (r.month < 6) quarters.Q2.push(r.return);
        else if (r.month < 9) quarters.Q3.push(r.return);
        else quarters.Q4.push(r.return);
    });

    return Object.entries(quarters).map(([q, rets]) => ({
        quarter: q,
        avg: rets.length ? rets.reduce((a, b) => a + b, 0) / rets.length : 0,
        greenPct: rets.length ? (rets.filter(r => r > 0).length / rets.length * 100) : 0,
        count: rets.length
    }));
}

function calcStreak(monthlyReturns) {
    if (!monthlyReturns.length) return { streak: 0, type: 'none' };
    // Sort by date descending
    const sorted = [...monthlyReturns].sort((a, b) => b.year - a.year || b.month - a.month);
    const first = sorted[0];
    let streak = 1;
    const type = first.return >= 0 ? 'green' : 'red';
    for (let i = 1; i < sorted.length; i++) {
        const isGreen = sorted[i].return >= 0;
        if ((type === 'green' && isGreen) || (type === 'red' && !isGreen)) {
            streak++;
        } else {
            break;
        }
    }
    return { streak, type, current: first };
}

function renderCalendar(coinData) {
    const container = document.getElementById('calendarContent');
    if (!container) return;

    let html = '';

    Object.entries(coinData).forEach(([coin, data]) => {
        const { returns, seasonality, quarterly, streak, median } = data;

        html += `<div class="cal-coin-section">
            <h3>${coin.replace('USDT', '')}</h3>

            <!-- Key Stats -->
            <div class="cal-stats-row">
                <div class="cal-stat">
                    <div class="cal-stat-label">Median Monthly</div>
                    <div class="cal-stat-value ${median >= 0 ? 'price-up' : 'price-down'}">${median >= 0 ? '+' : ''}${median.toFixed(1)}%</div>
                </div>
                <div class="cal-stat">
                    <div class="cal-stat-label">Current Streak</div>
                    <div class="cal-stat-value ${streak.type === 'green' ? 'price-up' : 'price-down'}">${streak.streak} ${streak.type} months</div>
                </div>
                <div class="cal-stat">
                    <div class="cal-stat-label">Best Month</div>
                    <div class="cal-stat-value">${MONTH_NAMES[seasonality.reduce((best, m) => m.avg > seasonality[best].avg ? seasonality.indexOf(m) : best, 0)]}</div>
                </div>
                <div class="cal-stat">
                    <div class="cal-stat-label">Worst Month</div>
                    <div class="cal-stat-value">${MONTH_NAMES[seasonality.reduce((worst, m) => m.avg < seasonality[worst].avg ? seasonality.indexOf(m) : worst, 0)]}</div>
                </div>
            </div>

            <!-- Heatmap -->
            <div class="cal-heatmap">
                <div class="cal-heatmap-header">
                    <div></div>
                    ${MONTH_NAMES.map(m => `<div class="cal-month-label">${m}</div>`).join('')}
                </div>`;

        // Group by year
        const byYear = {};
        returns.forEach(r => {
            if (!byYear[r.year]) byYear[r.year] = {};
            byYear[r.year][r.month] = r;
        });

        Object.keys(byYear).sort().forEach(year => {
            html += `<div class="cal-year-label">${year}</div>`;
            for (let m = 0; m < 12; m++) {
                const r = byYear[year]?.[m];
                if (r) {
                    const intensity = Math.min(Math.abs(r.return) / 15, 1);
                    const color = r.return >= 0
                        ? `rgba(63, 185, 80, ${0.2 + intensity * 0.8})`
                        : `rgba(248, 81, 73, ${0.2 + intensity * 0.8})`;
                    html += `<div class="cal-cell" style="background:${color}" title="${MONTH_NAMES[m]} ${year}: ${r.return >= 0 ? '+' : ''}${r.return.toFixed(1)}%">
                        ${r.return >= 0 ? '+' : ''}${r.return.toFixed(0)}%
                    </div>`;
                } else {
                    html += `<div class="cal-cell cal-empty">—</div>`;
                }
            }
        });

        html += `</div>`;

        <!-- Seasonality -->
        html += `<div class="cal-seasonality">
            <h4>Seasonality (Avg Return by Month)</h4>
            <div class="cal-bar-chart">`;

        const maxAbs = Math.max(...seasonality.map(s => Math.abs(s.avg)), 1);
        seasonality.forEach(s => {
            const pct = (s.avg / maxAbs) * 50;
            const color = s.avg >= 0 ? 'var(--green)' : 'var(--red)';
            html += `<div class="cal-bar-row">
                <span class="cal-bar-label">${MONTH_NAMES[s.month]}</span>
                <div class="cal-bar-track">
                    <div class="cal-bar-fill" style="width:${Math.abs(pct) + 1}%;background:${color}"></div>
                </div>
                <span class="cal-bar-value ${s.avg >= 0 ? 'price-up' : 'price-down'}">${s.avg >= 0 ? '+' : ''}${s.avg.toFixed(1)}%</span>
            </div>`;
        });

        html += `</div></div>`;

        <!-- Quarterly -->
        html += `<div class="cal-quarterly">
            <h4>Quarterly Performance</h4>
            <div class="cal-stats-row">`;

        quarterly.forEach(q => {
            html += `<div class="cal-stat">
                <div class="cal-stat-label">${q.quarter}</div>
                <div class="cal-stat-value ${q.avg >= 0 ? 'price-up' : 'price-down'}">${q.avg >= 0 ? '+' : ''}${q.avg.toFixed(1)}%</div>
                <div class="cal-stat-detail">${q.greenPct.toFixed(0)}% green</div>
            </div>`;
        });

        html += `</div></div></div>`;
    });

    container.innerHTML = html;
}

async function loadCalendar() {
    const container = document.getElementById('calendarContent');
    if (container) container.innerHTML = '<div class="loading">Loading calendar data...</div>';

    const coinData = {};

    for (const coin of CAL_COINS) {
        const klines = await fetchMonthlyKlines(coin, 36);
        if (!klines.length) continue;

        const returns = calcMonthlyReturns(klines);
        const seasonality = calcSeasonality(returns);
        const quarterly = calcQuarterly(returns);
        const streak = calcStreak(returns);

        // Calculate median
        const sortedReturns = returns.map(r => r.return).sort((a, b) => a - b);
        const mid = Math.floor(sortedReturns.length / 2);
        const median = sortedReturns.length % 2 ? sortedReturns[mid] : (sortedReturns[mid - 1] + sortedReturns[mid]) / 2;

        coinData[coin] = { returns, seasonality, quarterly, streak, median };
    }

    renderCalendar(coinData);
}

// Auto-load when calendar tab is shown
function initCalendar() {
    loadCalendar();
}
