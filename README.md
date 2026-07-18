# Crypto Oscillator Dashboard

A live crypto dashboard built on the **VirtualBacon Altcoin Oscillator Thesis** with real-time Binance API data.

## What It Does

- **Portfolio Tracker** — Live prices, RSI, entry/exit zones, and stop loss alerts for 7 coins
- **ALT/BTC Ratio Monitor** — Real-time ratios for S/A tier coins vs Bitcoin
- **Sector Correlation** — Detects when AI, RWA, L1, or Meme sectors move together
- **Trading Plan** — Visual display of portfolio allocation and entry zones
- **VirtualBacon Tier List** — S/A/B/F tier classification with performance data
- **Auto-Refresh** — Updates every 5 minutes automatically

## The Strategy

Based on VirtualBacon's Altcoin Oscillator Rank (April 10, 2026):

| Tier | Coins | Strategy |
|------|-------|----------|
| **S Tier** | FET, TRX, RENDER, ZEC | Core positions — highest conviction |
| **A Tier** | SOL, ETH, BNB, XMR, XRP, FLOKI | Tactical — strong oscillators |
| **F Tier** | 54 coins (78%) | Avoid — permanently broken vs BTC |

### Entry Rules
- Buy when USDT pair is within 5-10% of 52-week low
- This corresponds to ALT/BTC ratio hitting support
- Use Mean Reversion (BB+RSI) as primary strategy

### Exit Rules
- Take profit at 10-20% below 52-week high
- Hard stop at 52-week low (thesis broken)

## Tech Stack

- **Frontend:** Vanilla HTML/CSS/JS (no framework dependencies)
- **Data:** Binance API (live prices, klines, 24hr stats)
- **Hosting:** Firebase Hosting
- **Style:** Dark theme, responsive design

## Local Development

```bash
# Serve locally
cd crypto-dashboard/public
python3 -m http.server 8080

# Open http://localhost:8080
```

## Deployment

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Deploy
cd crypto-dashboard
firebase deploy
```

## Configuration

Edit `app.js` to modify:
- `PORTFOLIO` — Add/remove coins and entry zones
- `ALTBTC_PAIRS` — ALT/BTC pairs to monitor
- `SECTORS` — Sector groupings for correlation
- `TIER_DATA` — VirtualBacon tier classifications

## Files

```
crypto-dashboard/
├── public/
│   ├── index.html      # Main dashboard
│   ├── styles.css      # Dark theme styles
│   └── app.js          # API calls + rendering
├── firebase.json       # Firebase hosting config
├── .firebaserc         # Firebase project ID
└── README.md           # This file
```

## Data Sources

| Source | Data | Update Frequency |
|--------|------|-----------------|
| Binance API | Live prices, klines, 24hr stats | Real-time (5min refresh) |
| VirtualBacon | Tier classifications | April 2026 (static) |
| HunterAlphaBot | Trading plan, entry zones | Manual updates |

## Disclaimer

⚠️ **Not financial advice.** This is a research tool. Cryptocurrency trading involves substantial risk. Always DYOR (Do Your Own Research).

## Credits

- **VirtualBacon** — Altcoin Oscillator Thesis (April 10, 2026)
- **Binance** — Market data API
- **HunterAlphaBot** — Strategy development and automation
