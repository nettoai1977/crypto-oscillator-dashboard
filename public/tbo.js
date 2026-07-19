/* TBO-Style Trend Indicator — Dashboard Integration */

const TBO_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'FETUSDT', 'XRPUSDT', 'BNBUSDT'];
const TBO_INTERVALS = [
    { key: '1w', label: 'Weekly', limit: 100 },
    { key: '1d', label: 'Daily', limit: 200 },
    { key: '4h', label: '4-Hour', limit: 200 },
    { key: '1h', label: '1-Hour', limit: 200 },
];

function tboEma(values, period) {
    const alpha = 2 / (period + 1);
    const out = [];
    let cur = null;
    for (const v of values) {
        cur = cur === null ? v : alpha * v + (1 - alpha) * cur;
        out.push(cur);
    }
    return out;
}

async function fetchTboKlines(symbol, interval, limit) {
    try {
        const r = await fetch(`${BINANCE_API}/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`);
        const data = await r.json();
        return data.map(k => ({
            open: parseFloat(k[1]), high: parseFloat(k[2]),
            low: parseFloat(k[3]), close: parseFloat(k[4]),
        }));
    } catch { return []; }
}

function calcTbo(rows, fastPeriod = 20, slowPeriod = 50) {
    if (rows.length < slowPeriod + 10) return null;
    const mids = rows.map(r => (r.high + r.low) / 2);
    const fast = tboEma(mids, fastPeriod);
    const slow = tboEma(fast, slowPeriod);
    const closes = rows.map(r => r.close);

    const last = closes.length - 1;
    const prev = last - 1;
    const px = closes[last];
    const f = fast[last];
    const s = slow[last];

    let cloudStatus, signal, trend;
    if (px > Math.max(f, s)) cloudStatus = 'ABOVE';
    else if (px < Math.min(f, s)) cloudStatus = 'BELOW';
    else cloudStatus = 'IN';

    trend = f > s ? 'BULLISH' : 'BEARISH';

    if (cloudStatus === 'ABOVE' && trend === 'BULLISH') signal = 'STRONG_BULL';
    else if (cloudStatus === 'BELOW' && trend === 'BEARISH') signal = 'STRONG_BEAR';
    else if (cloudStatus === 'ABOVE' && trend === 'BEARISH') signal = 'WEAK_BULL';
    else signal = 'WEAK_BEAR';

    const deviation = f > 0 ? ((px - f) / f * 100) : 0;
    const trendChanged = (fast[last] > slow[last]) !== (fast[prev] > slow[prev]);

    // Adaptive support
    const lookback = Math.min(20, last);
    const recentLows = rows.slice(last - lookback, last).map(r => r.low);
    const support = Math.min(...recentLows) * 1.02;

    return { signal, trend, cloudStatus, deviation, fast: f, slow: s, support, trendChanged, price: px };
}

async function loadTbo() {
    const container = document.getElementById('tboContent');
    if (container) container.innerHTML = '<div class="loading">Running multi-timeframe analysis...</div>';

    const results = {};

    for (const symbol of TBO_SYMBOLS) {
        results[symbol] = [];
        for (const tf of TBO_INTERVALS) {
            const rows = await fetchTboKlines(symbol, tf.key, tf.limit);
            const tbo = calcTbo(rows);
            if (tbo) {
                results[symbol].push({ ...tbo, timeframe: tf.label });
            }
        }
    }

    renderTbo(results);
}

function signalIcon(signal) {
    const map = {
        'STRONG_BULL': { icon: '🟢🟢', label: 'STRONG BULL', cls: 'price-up' },
        'WEAK_BULL': { icon: '🟢', label: 'WEAK BULL', cls: 'price-up' },
        'STRONG_BEAR': { icon: '🔴🔴', label: 'STRONG BEAR', cls: 'price-down' },
        'WEAK_BEAR': { icon: '🔴', label: 'WEAK BEAR', cls: 'price-down' },
    };
    return map[signal] || { icon: '⚪', label: 'MIXED', cls: '' };
}

function renderTbo(data) {
    const container = document.getElementById('tboContent');
    if (!container) return;

    let html = '';

    Object.entries(data).forEach(([symbol, timeframes]) => {
        if (!timeframes.length) return;
        const coin = symbol.replace('USDT', '');
        const last = timeframes[timeframes.length - 1];
        const bullCount = timeframes.filter(t => t.signal.includes('BULL')).length;
        const bearCount = timeframes.filter(t => t.signal.includes('BEAR')).length;
        const verdict = bullCount > bearCount ? { text: 'BULLISH', cls: 'price-up', icon: '🟢' }
            : bearCount > bullCount ? { text: 'BEARISH', cls: 'price-down', icon: '🔴' }
            : { text: 'MIXED', cls: '', icon: '⚪' };

        html += `<div class="tbo-coin">
            <div class="tbo-coin-header">
                <h3>${coin}</h3>
                <span class="tbo-verdict ${verdict.cls}">${verdict.icon} ${verdict.text}</span>
            </div>
            <div class="tbo-timeframes">
                <div class="tbo-tf-header">
                    <span>TF</span><span>Price</span><span>Fast</span><span>Cloud</span><span>Signal</span><span>Dev%</span>
                </div>`;

        timeframes.forEach(tf => {
            const sig = signalIcon(tf.signal);
            html += `<div class="tbo-tf-row ${tf.trendChanged ? 'tbo-trend-change' : ''}">
                <span class="tbo-tf-label">${tf.timeframe}</span>
                <span>$${tf.price.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
                <span style="color:var(--text-muted)">$${tf.fast.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</span>
                <span style="color:${tf.cloudStatus === 'ABOVE' ? 'var(--green)' : tf.cloudStatus === 'BELOW' ? 'var(--red)' : 'var(--orange)'}">${tf.cloudStatus}</span>
                <span class="${sig.cls}">${sig.icon} ${sig.label}</span>
                <span class="${tf.deviation > 0 ? 'price-up' : 'price-down'}">${tf.deviation > 0 ? '+' : ''}${tf.deviation.toFixed(1)}%</span>
            </div>`;

            if (tf.trendChanged) {
                html += `<div class="tbo-alert">⚡ Trend change on ${tf.timeframe}!</div>`;
            }
        });

        if (Math.abs(last.deviation) > 15) {
            html += `<div class="tbo-alert">⚠️ Overextended ${last.deviation > 0 ? 'above' : 'below'} fast line (${last.deviation.toFixed(1)}%) — watch for mean reversion</div>`;
        }

        html += `</div></div>`;
    });

    container.innerHTML = html;
}

function initTbo() {
    loadTbo();
}
