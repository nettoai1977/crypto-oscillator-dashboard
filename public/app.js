/* Crypto Oscillator Dashboard — App Logic */

const BINANCE_API = 'https://api.binance.com/api/v3';

// Portfolio configuration
const PORTFOLIO = [
    { symbol: 'FETUSDT', coin: 'FET', tier: 'S', alloc: '25%', entryLow: 0.1564, entryHigh: 0.1720, stop: 0.1500 },
    { symbol: 'SOLUSDT', coin: 'SOL', tier: 'A', alloc: '20%', entryLow: 74.50, entryHigh: 81.95, stop: 70.00 },
    { symbol: 'RENDERUSDT', coin: 'RENDER', tier: 'S', alloc: '15%', entryLow: 1.456, entryHigh: 1.602, stop: 1.40 },
    { symbol: 'XRPUSDT', coin: 'XRP', tier: 'A', alloc: '15%', entryLow: 1.084, entryHigh: 1.192, stop: 1.00 },
    { symbol: 'BNBUSDT', coin: 'BNB', tier: 'A', alloc: '10%', entryLow: 566.25, entryHigh: 622.88, stop: 540.00 },
    { symbol: 'ONDOUSDT', coin: 'ONDO', tier: 'SPEC', alloc: '10%', entryLow: 0.30, entryHigh: 0.38, stop: 0.25 },
    { symbol: 'INJUSDT', coin: 'INJ', tier: 'SPEC', alloc: '5%', entryLow: 0, entryHigh: 999999, stop: 0 },
];

const ALTBTC_PAIRS = [
    { symbol: 'ETHBTC', name: 'ETH/BTC' },
    { symbol: 'SOLBTC', name: 'SOL/BTC' },
    { symbol: 'XRPBTC', name: 'XRP/BTC' },
    { symbol: 'BNBBTC', name: 'BNB/BTC' },
    { symbol: 'TRXBTC', name: 'TRX/BTC' },
    { symbol: 'FETBTC', name: 'FET/BTC' },
    { symbol: 'RENDERBTC', name: 'RENDER/BTC' },
];

const SECTORS = {
    'AI': ['FETUSDT', 'RENDERUSDT', 'TAOUSDT', 'AKTUSDT'],
    'RWA': ['ONDOUSDT'],
    'L1': ['SOLUSDT', 'ETHUSDT', 'AVAXUSDT', 'NEARUSDT'],
    'MEME': ['DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT', 'WIFUSDT', 'FLOKIUSDT'],
};

const TIER_DATA = {
    S: [
        { coin: 'FET', vsLast: '+119.7%', aboveFloor: '+65.3%' },
        { coin: 'TRX', vsLast: '+49.7%', aboveFloor: '+212.1%' },
        { coin: 'RENDER', vsLast: '+41.1%', aboveFloor: '+96.0%' },
        { coin: 'ZEC', vsLast: '+23.7%', aboveFloor: '+1595.7%' },
    ],
    A: [
        { coin: 'BNB', vsLast: '-6.6%', aboveFloor: '+58.8%' },
        { coin: 'FLOKI', vsLast: '-10.0%', aboveFloor: '+48.1%' },
        { coin: 'XRP', vsLast: '-12.5%', aboveFloor: '+165.4%' },
        { coin: 'XMR', vsLast: '-12.9%', aboveFloor: '+203.3%' },
        { coin: 'SOL', vsLast: '-29.8%', aboveFloor: '+182.0%' },
        { coin: 'ETH', vsLast: '-31.5%', aboveFloor: '+70.6%' },
    ],
    B: [
        { coin: 'MKR', vsLast: '-46.8%', aboveFloor: '+63.2%' },
        { coin: 'XLM', vsLast: '-62.4%', aboveFloor: '+65.6%' },
        { coin: 'BCH', vsLast: '-63.1%', aboveFloor: '+91.7%' },
        { coin: 'QNT', vsLast: '-63.7%', aboveFloor: '+65.9%' },
        { coin: 'HBAR', vsLast: '-64.9%', aboveFloor: '+100.0%' },
    ],
    F: [
        'FLOW', 'FIL', 'ONE', 'SUSHI', 'AXS', 'EOS', '1INCH', 'GALA', 'COMP', 'CAKE', 'CRV', 'SAND',
        'ALGO', 'KAVA', 'JASMY', 'MANA', 'ZIL', 'NEO', 'XTZ', 'DASH', 'SNX', 'THETA', 'EGLD', 'BAT',
        'CRO', 'GRT', 'DOT', 'VET', 'ICP', 'CHZ', 'FTM', 'ADA', 'ROSE', 'ATOM', 'LTC', 'NEAR',
        'AAVE', 'ETC', 'UNI', 'RUNE', 'BSV', 'DYDX', 'MINA', 'AVAX', 'DOGE', 'POL', 'LINK', 'SHIB',
        'IMX', 'ENS', 'LDO', 'STX', 'CFX', 'INJ',
    ],
};

// Fetch helpers
async function fetchTicker(symbol) {
    try {
        const r = await fetch(`${BINANCE_API}/ticker/24hr?symbol=${symbol}`);
        return await r.json();
    } catch (e) {
        console.error(`Failed to fetch ${symbol}:`, e);
        return null;
    }
}

async function fetchKlines(symbol, interval = '1h', limit = 100) {
    try {
        const r = await fetch(`${BINANCE_API}/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`);
        const data = await r.json();
        return data.map(k => parseFloat(k[4]));
    } catch (e) {
        return [];
    }
}

function calcRSI(closes, period = 14) {
    if (closes.length < period + 1) return 50;
    const gains = [], losses = [];
    for (let i = 1; i < closes.length; i++) {
        const diff = closes[i] - closes[i - 1];
        gains.push(Math.max(diff, 0));
        losses.push(Math.max(-diff, 0));
        if (gains.length > period) { gains.shift(); losses.shift(); }
    }
    const avgGain = gains.reduce((a, b) => a + b, 0) / gains.length;
    const avgLoss = losses.reduce((a, b) => a + b, 0) / losses.length;
    const rs = avgLoss === 0 ? 999 : avgGain / avgLoss;
    return 100 - 100 / (1 + rs);
}

function formatPrice(price) {
    if (price >= 1000) return '$' + price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 1) return '$' + price.toFixed(4);
    if (price >= 0.01) return '$' + price.toFixed(6);
    return '$' + price.toFixed(8);
}

function formatPercent(pct) {
    const sign = pct >= 0 ? '+' : '';
    return sign + pct.toFixed(2) + '%';
}

// Render functions
function renderPortfolio(data) {
    const tbody = document.getElementById('portfolioBody');
    let html = '';
    let entryCount = 0;
    let signalCount = 0;

    data.forEach(item => {
        if (!item.ticker) return;

        const price = parseFloat(item.ticker.lastPrice);
        const change = parseFloat(item.ticker.priceChangePercent);
        const rsi = item.rsi;
        const info = item.info;

        // Determine status
        let status = 'badge-wait';
        let statusText = 'Wait';
        if (price <= info.entryHigh && price >= info.entryLow) {
            status = 'badge-entry';
            statusText = '🟢 Entry Zone';
            entryCount++;
        } else if (price < info.entryLow) {
            status = 'badge-entry';
            statusText = '🟢 Below Entry';
            entryCount++;
        } else if (info.stop > 0 && price <= info.stop) {
            status = 'badge-stop';
            statusText = '⚠️ STOP';
            signalCount++;
        }

        if (rsi > 70) {
            signalCount++;
            status = 'badge-overbought';
            statusText = '🔴 Overbought';
        } else if (rsi < 30) {
            signalCount++;
            status = 'badge-entry';
            statusText = '🟢 Oversold';
        }

        const tierClass = `badge-tier-${info.tier.toLowerCase()}`;
        const priceClass = change >= 0 ? 'price-up' : 'price-down';

        html += `<tr>
            <td><strong>${info.coin}</strong></td>
            <td><span class="badge ${tierClass}">${info.tier}</span></td>
            <td>${formatPrice(price)}</td>
            <td class="${priceClass}">${formatPercent(change)}</td>
            <td>${rsi.toFixed(1)}</td>
            <td style="font-size:0.8rem;color:var(--text-muted)">${formatPrice(info.entryLow)} — ${formatPrice(info.entryHigh)}</td>
            <td><span class="badge ${status}">${statusText}</span></td>
            <td>${info.alloc}</td>
        </tr>`;
    });

    tbody.innerHTML = html;

    // Update summary cards
    document.getElementById('entryCount').textContent = `${entryCount}/7`;
    document.getElementById('entryDetail').textContent = entryCount > 3 ? '⚠️ Market-wide dip' : 'Selectively at support';
    document.getElementById('signalCount').textContent = signalCount;
    document.getElementById('signalDetail').textContent = signalCount > 0 ? 'Check RSI & stops' : 'All clear';
}

function renderALTBTC(data) {
    const tbody = document.getElementById('altrbtcBody');
    let html = '';

    data.forEach(item => {
        if (!item.ticker) return;

        const ratio = parseFloat(item.ticker.lastPrice);
        const change = parseFloat(item.ticker.priceChangePercent);
        const trend = change >= 0 ? '🟢' : '🔴';
        const signal = ratio < 0.001 ? '🟢 Near support' : '⚪ Mid-range';

        html += `<tr>
            <td><strong>${item.name}</strong></td>
            <td>${ratio.toFixed(8)}</td>
            <td class="${change >= 0 ? 'price-up' : 'price-down'}">${formatPercent(change)}</td>
            <td>${trend}</td>
            <td>${signal}</td>
        </tr>`;
    });

    tbody.innerHTML = html;
}

function renderSectors(data) {
    const container = document.getElementById('sectorContent');
    let html = '';

    Object.entries(data).forEach(([name, tokens]) => {
        const validTokens = tokens.filter(t => t.ticker);
        if (validTokens.length === 0) return;

        const avgChange = validTokens.reduce((sum, t) => sum + parseFloat(t.ticker.priceChangePercent), 0) / validTokens.length;
        const allSameDir = validTokens.every(t => parseFloat(t.ticker.priceChangePercent) > 0) ||
                          validTokens.every(t => parseFloat(t.ticker.priceChangePercent) < 0);
        const correlated = allSameDir && Math.abs(avgChange) > 2;

        html += `<div class="sector-card ${correlated ? 'sector-correlated' : ''}">
            <h4>${name}</h4>
            <div class="avg-change ${avgChange >= 0 ? 'price-up' : 'price-down'}">${formatPercent(avgChange)}</div>
            <div class="tokens">${validTokens.map(t => `${t.coin}: ${formatPercent(parseFloat(t.ticker.priceChangePercent))}`).join(' • ')}</div>
            ${correlated ? '<div style="margin-top:4px;font-size:0.75rem;color:var(--green)">⚡ Correlated move — narrative signal</div>' : ''}
        </div>`;
    });

    container.innerHTML = html;
}

function renderTiers() {
    ['S', 'A', 'B'].forEach(tier => {
        const container = document.getElementById(`tier${tier}`);
        container.innerHTML = TIER_DATA[tier].map(c =>
            `<div class="tier-coin"><span class="coin-name">${c.coin}</span><span class="coin-change">${c.vsLast} vs BTC</span></div>`
        ).join('');
    });

    // F tier
    document.getElementById('tierFFull').innerHTML = TIER_DATA.F.map(c =>
        `<span style="display:inline-block;padding:2px 6px;margin:2px;background:var(--bg-card);border-radius:4px;font-size:0.7rem">${c}</span>`
    ).join('');
}

function toggleTierF() {
    const el = document.getElementById('tierFFull');
    el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

// Main refresh
async function refreshAll() {
    document.getElementById('lastUpdated').textContent = 'Refreshing...';

    // Fetch portfolio data
    const portfolioData = await Promise.all(PORTFOLIO.map(async (info) => {
        const ticker = await fetchTicker(info.symbol);
        const closes = await fetchKlines(info.symbol);
        const rsi = calcRSI(closes);
        return { info, ticker, rsi };
    }));

    // Fetch ALT/BTC data
    const altrbtcData = await Promise.all(ALTBTC_PAIRS.map(async (pair) => {
        const ticker = await fetchTicker(pair.symbol);
        return { name: pair.name, ticker };
    }));

    // Fetch sector data
    const sectorData = {};
    for (const [name, coins] of Object.entries(SECTORS)) {
        sectorData[name] = await Promise.all(coins.map(async (symbol) => {
            const ticker = await fetchTicker(symbol);
            const coin = symbol.replace('USDT', '');
            return { coin, ticker };
        }));
    }

    // Fetch BTC for summary
    const btcTicker = await fetchTicker('BTCUSDT');
    if (btcTicker) {
        document.getElementById('btcPrice').textContent = formatPrice(parseFloat(btcTicker.lastPrice));
        const btcChange = parseFloat(btcTicker.priceChangePercent);
        document.getElementById('btcChange').textContent = formatPercent(btcChange) + ' (24h)';
        document.getElementById('btcChange').className = `card-detail ${btcChange >= 0 ? 'price-up' : 'price-down'}`;
    }

    // Determine market status
    const entryCount = portfolioData.filter(d => d.ticker && parseFloat(d.ticker.lastPrice) <= d.info.entryHigh).length;
    const marketStatus = document.getElementById('marketStatus');
    const marketDetail = document.getElementById('marketDetail');
    if (entryCount >= 5) {
        marketStatus.textContent = '🟢 DIP';
        marketDetail.textContent = 'Majority at support — DCA zone';
    } else if (entryCount >= 3) {
        marketStatus.textContent = '🟡 MIXED';
        marketDetail.textContent = 'Some coins at support';
    } else {
        marketStatus.textContent = '🔴 HIGH';
        marketDetail.textContent = 'Few coins at entry — wait';
    }

    // Render everything
    renderPortfolio(portfolioData);
    renderALTBTC(altrbtcData);
    renderSectors(sectorData);
    renderTiers();

    document.getElementById('lastUpdated').textContent = `Updated: ${new Date().toLocaleString()}`;
}

// Init
refreshAll();

// Auto-refresh every 5 minutes
setInterval(refreshAll, 5 * 60 * 1000);
