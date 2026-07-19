# What We Took From Mastering Assets / Better Traders

## What We Extracted (Useful Parts)

### 1. DCA Bot Concept (改良版 — Improved)
The core idea of automated buying at intervals is sound, but we fixed the flaws:

**Their Martingale DCA (Risky):**
- Double down when losing (dangerous)
- No stop loss (blow-up risk)
- No position limit (unlimited averaging)
- 1-3-7 ladder with no caps

**Our Improved DCA (Safe):**
- ✅ Hard stop loss at 15% below average
- ✅ Max position limit (prevents unlimited averaging)
- ✅ Position sizing caps (never more than 25% per buy)
- ✅ Three variants: Conservative (1x), Balanced (1.5x), Aggressive (2x)

### 2. Pair Selection via Data
Their "5 years of data" approach for selecting pairs is valid. We implemented:
- Backtest across multiple timeframes
- Win rate tracking per pair
- Volatility-based pair filtering

### 3. Portfolio Allocation Principles
Their Module 4 on allocation is useful:
- Don't put all capital in one bot
- Diversify across pairs
- Balance risk between aggressive and conservative positions

### 4. The "Command Center" Concept
Their emphasis on monitoring and managing bot positions (Module 6) is valid:
- Don't just set and forget
- Monitor open positions
- Edit parameters when market conditions change
- Strategic intervention when needed

## What We Rejected (Dangerous Parts)

### 1. Martingale (Doubling Down)
❌ When you double down after losses, you amplify risk exponentially
❌ One black swan event blows up the entire portfolio
❌ This is what killed Alameda/FTX's risk model

### 2. "24/7 Automated Gains" Marketing
❌ Bots don't print money — they work in certain conditions
❌ DCA bots bleed in sustained downtrends
❌ Marketing overpromises

### 3. Overfitted Backtests
❌ Their backtests may use cherry-picked periods
❌ Our system uses live Binance data (real-time, not curated)

### 4. No Risk Management
❌ No stop losses in their core strategy
❌ No max drawdown limits
❌ No "what if BTC drops 50%" scenario

## Backtest Results — DCA with Safety

Tested on 365 daily candles (Binance live data):

| Pair | Conservative | Balanced | Aggressive | Best |
|------|-------------|----------|------------|------|
| BTC | -$57 (-1.2%) | -$71 (-1.5%) | -$119 (-2.5%) | Conservative |
| ETH | +$3 (0%) | -$48 (-1.1%) | +$24 (+0.3%) | Aggressive |
| SOL | -$85 (-1.8%) | -$108 (-2.3%) | -$344 (-7.2%) | Conservative |
| XRP | -$51 (-1.1%) | -$65 (-1.5%) | +$49 (+0.7%) | Aggressive |
| FET | -$210 (-4.3%) | -$66 (-1.5%) | -$111 (-2.5%) | Balanced |
| BNB | +$12 (+0.2%) | +$34 (+0.6%) | +$63 (+1.2%) | Aggressive |
| ONDO | -$60 (-1.3%) | -$180 (-3.8%) | -$251 (-5.3%) | Conservative |

**Key Insight:** Even with safety improvements, DCA bots mostly lose in a bear/sideways market. The only winners were BNB (tight range) and XRP/ETH (aggressive variant caught a bounce).

## When to Use DCA vs Mean Reversion

| Market Condition | Best Strategy | Why |
|-----------------|--------------|-----|
| Sideways/ranging | DCA bots | Small oscillations = consistent small wins |
| Oversold bounce | Mean Reversion | RSI < 35 + BB lower band = high probability entry |
| Strong uptrend | Trend following | EMA crossover captures the move |
| Sustained downtrend | Cash / short | DCA bleeds, Mean Rev gets stopped out |

## Updated Trading Plan Integration

| Strategy | When to Use | Coins | Allocation |
|----------|------------|-------|-----------|
| **Mean Reversion BB+RSI** | Default (works in most conditions) | FET, SOL, XRP, RENDER | 60% |
| **DCA Bots (改良版)** | Sideways market only | BNB, XRP | 15% (side allocation) |
| **Trend Following** | Strong uptrend confirmed | FLOKI, BTC | 15% |
| **Cash/Stablecoin** | Uncertainty / downtrend | — | 10% (dry powder) |

## Source
- Mastering Assets (masteringassets.com) — Aaron Dishner
- The Better Traders (thebettertraders.com) — Aaron Dishner
- Backtested: July 19, 2026 — HunterAlphaBot
