# Crypto Trading Plan — July 19, 2026

## Portfolio Allocation Framework

### Core (60%) — Oscillator Thesis + Backtest Data
Highest probability based on VirtualBacon framework and Binance backtesting.

| Coin | Tier | Entry Zone | Strategy | Allocation | Why |
|------|------|-----------|----------|-----------|-----|
| **FET** | S | $0.156-$0.172 | Mean Reversion BB+RSI | 25% | Strongest oscillator (+119.7% vs BTC), AI compute narrative, best backtest results (+$273) |
| **SOL** | A | $74.50-$81.95 | Mean Reversion BB+RSI | 20% | +182% above floor, ALT/BTC at 0% support, backtest +$175, lowest max DD (1.4%) |
| **RENDER** | S | $1.46-$1.60 | Mean Reversion BB+RSI | 15% | S-tier (+41.1% vs BTC), GPU/AI narrative, backtest +$114 |

### Tactical (25%) — ALT/BTC at Support
Strong bounce history, currently at support levels.

| Coin | Tier | Entry Zone | Strategy | Allocation | Why |
|------|------|-----------|----------|-----------|-----|
| **XRP** | A | $1.08-$1.19 | Mean Reversion BB+RSI | 15% | ALT/BTC at 0%, backtest +$117, institutional wildcard |
| **BNB** | A | $566-$623 | Mean Reversion BB+RSI | 10% | ALT/BTC at 0%, tightest range, exchange token safety |

### Speculative (15%) — Thesis-Driven Bets
Asymmetric upside, higher risk, based on fundamentals not oscillator data.

| Coin | Thesis | Entry Zone | Allocation | Why |
|------|--------|-----------|-----------|-----|
| **ONDO** | Tokenization legislation | $0.30-$0.38 | 10% | SEC cleared, live BlackRock ETF, DTC pilot, former House Financial Services Chair on team. CLARITY Act passes = repricing. |
| **INJ** | F-tier revenge cycle | Current levels | 5% | +130% vs last cycle, DEX infra, contrarian play |

## Rules

1. **Entry:** DCA in over 4-6 weeks (don't buy all at once)
2. **Core positions:** Only enter within 5-10% of 52-week low
3. **Stop loss:** If a coin breaks below 52-week low, thesis is wrong — exit
4. **Take profit:** Scale out at 10-20% below 52-week high
5. **Review:** Re-run backtest monthly, update tiers quarterly
6. **No leverage:** All spot positions only
7. **Max single position:** 25% of portfolio (FET cap)

## Risk Management

| Rule | Detail |
|------|--------|
| Max portfolio risk | No more than you can afford to lose entirely |
| Correlation risk | FET + RENDER are correlated (AI/GPU narrative) — cap combined at 40% |
| Legislative risk | ONDO is a binary bet — size accordingly (10% max) |
| Rebalance | Monthly — if a coin runs 50%+, trim back to target allocation |

## Monitoring Checklist

- [ ] Weekly: Check ALT/BTC ratios for S/A tier coins
- [ ] Monthly: Re-run Binance backtest script
- [ ] Quarterly: Review VirtualBacon tier updates (if published)
- [ ] Ongoing: Track CLARITY Act / Tokenization Act progress
- [ ] Ongoing: Watch for ONDO SEC registration approval

## Data Sources

| Source | Purpose | Updated |
|--------|---------|---------|
| VirtualBacon Altcoin Oscillator Rank | Tier classification | April 10, 2026 |
| Binance API backtest v2 | Strategy validation | Live (real-time) |
| ALT/BTC ratio analysis | Entry/exit signals | Live (real-time) |
| US legislation tracker | ONDO thesis | Ongoing |

## Key Files

- `knowledge/virtualbacon-altcoin-oscillator-rank.md` — Full tier list + analysis
- `binance_testnet_v2.py` — Backtest script
- `binance_testnet_experiments.py` — Original backtest script

---
*Created: July 19, 2026*
*Author: HunterAlphaBot*
