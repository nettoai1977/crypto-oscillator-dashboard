#!/usr/bin/env python3
"""
Binance Backtester v2 — VirtualBacon Oscillator Integration
Adds S/A tier pairs + ALT/BTC ratio analysis
"""
import math, statistics, requests, json, time
from datetime import datetime

# VirtualBacon S Tier (outperformed BTC)
S_TIER = ["FETUSDT", "TRXUSDT", "RENDERUSDT", "ZECUSDT"]

# VirtualBacon A Tier (strong oscillators)
A_TIER = ["SOLUSDT", "ETHUSDT", "BNBUSDT", "XMRUSDT", "XRPUSDT", "FLOKIUSDT"]

# Original pairs (baseline)
BASELINE = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# Combined unique set for full run
ALL_PAIRS = ["BTCUSDT"] + list(set(S_TIER + A_TIER + ["ONDOUSDT"]))

# ALT/BTC ratio pairs — the truth per VirtualBacon
ALTBTC_PAIRS = ["ETHBTC", "SOLBTC", "XRPBTC", "BNBBTC", "TRXBTC"]

INTERVAL = "1h"
LIMIT = 1000
INITIAL_CAPITAL = 5000.0
FEE = 0.0004
SLIPPAGE = 0.0002
TRADE_COST = FEE + SLIPPAGE


def fetch_klines(symbol, interval="1h", limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    try:
        r = requests.get(url, params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=30)
        r.raise_for_status()
        data = r.json()
        rows = []
        for k in data:
            rows.append({
                "ts": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            })
        return rows
    except Exception as e:
        print(f"  ⚠ Failed to fetch {symbol}: {e}")
        return []


def ema(values, period):
    alpha = 2 / (period + 1)
    out = []
    cur = None
    for v in values:
        cur = v if cur is None else (alpha * v + (1 - alpha) * cur)
        out.append(cur)
    return out


def sma(values, period):
    out = []
    window = []
    for v in values:
        window.append(v)
        if len(window) > period:
            window.pop(0)
        out.append(sum(window) / len(window))
    return out


def stddev(values, period):
    out = []
    window = []
    for v in values:
        window.append(v)
        if len(window) > period:
            window.pop(0)
        out.append(statistics.pstdev(window) if len(window) > 1 else 0.0)
    return out


def rsi(values, period=14):
    gains, losses = [], []
    out = [50.0]
    for i in range(1, len(values)):
        diff = values[i] - values[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
        if len(gains) > period:
            gains.pop(0); losses.pop(0)
        avg_gain = sum(gains)/len(gains) if gains else 0
        avg_loss = sum(losses)/len(losses) if losses else 0
        rs = avg_gain/avg_loss if avg_loss else 999
        out.append(100 - 100/(1+rs))
    return out


def backtest_trend(rows, leverage=2.0, risk_frac=0.2):
    closes = [r['close'] for r in rows]
    e12 = ema(closes, 12)
    e48 = ema(closes, 48)
    capital = INITIAL_CAPITAL
    pos = 0; entry = 0.0; notional = 0.0
    equity_curve = []; trades = []
    for i in range(50, len(rows)):
        px = closes[i]
        signal = 1 if e12[i] > e48[i] else -1 if e12[i] < e48[i] else 0
        unreal = pos * (px - entry) / entry * notional if pos else 0.0
        equity_curve.append(capital + unreal)
        if pos == 0 and signal != 0:
            pos = signal
            notional = capital * risk_frac * leverage
            capital -= notional * TRADE_COST
            entry = px
            trades.append({"side": "LONG" if pos==1 else "SHORT", "entry": entry, "entry_i": i})
        elif pos != 0:
            ret = pos * (px - entry) / entry
            stop = -0.02 / leverage
            take = 0.035 / leverage
            if signal == -pos or ret <= stop or ret >= take:
                pnl = ret * notional
                capital += pnl
                capital -= notional * TRADE_COST
                trades[-1].update({"exit": px, "exit_i": i, "pnl": pnl})
                pos = 0; entry = 0.0; notional = 0.0
    return summarize("Trend EMA 12/48", rows, equity_curve, trades, capital)


def backtest_meanrev(rows, leverage=2.0, risk_frac=0.15):
    closes = [r['close'] for r in rows]
    mids = sma(closes, 20)
    sds = stddev(closes, 20)
    rs = rsi(closes, 14)
    capital = INITIAL_CAPITAL
    pos = 0; entry = 0.0; notional = 0.0
    equity_curve = []; trades = []
    for i in range(30, len(rows)):
        px = closes[i]
        upper = mids[i] + 2*sds[i]
        lower = mids[i] - 2*sds[i]
        signal = 0
        if px < lower and rs[i] < 35:
            signal = 1
        elif px > upper and rs[i] > 65:
            signal = -1
        unreal = pos * (px - entry) / entry * notional if pos else 0.0
        equity_curve.append(capital + unreal)
        if pos == 0 and signal != 0:
            pos = signal
            notional = capital * risk_frac * leverage
            capital -= notional * TRADE_COST
            entry = px
            trades.append({"side": "LONG" if pos==1 else "SHORT", "entry": entry, "entry_i": i})
        elif pos != 0:
            ret = pos * (px - entry) / entry
            exit_cond = (pos == 1 and px >= mids[i]) or (pos == -1 and px <= mids[i]) or ret <= (-0.015 / leverage) or ret >= (0.02 / leverage)
            if exit_cond:
                pnl = ret * notional
                capital += pnl
                capital -= notional * TRADE_COST
                trades[-1].update({"exit": px, "exit_i": i, "pnl": pnl})
                pos = 0; entry = 0.0; notional = 0.0
    return summarize("Mean Reversion BB+RSI", rows, equity_curve, trades, capital)


def backtest_breakout(rows, leverage=2.0, risk_frac=0.18):
    closes = [r['close'] for r in rows]
    highs = [r['high'] for r in rows]
    lows = [r['low'] for r in rows]
    capital = INITIAL_CAPITAL
    pos = 0; entry = 0.0; notional = 0.0
    equity_curve = []; trades = []
    for i in range(25, len(rows)):
        px = closes[i]
        hh = max(highs[i-20:i])
        ll = min(lows[i-20:i])
        signal = 1 if px > hh else -1 if px < ll else 0
        unreal = pos * (px - entry) / entry * notional if pos else 0.0
        equity_curve.append(capital + unreal)
        if pos == 0 and signal != 0:
            pos = signal
            notional = capital * risk_frac * leverage
            capital -= notional * TRADE_COST
            entry = px
            trades.append({"side": "LONG" if pos==1 else "SHORT", "entry": entry, "entry_i": i})
        elif pos != 0:
            ret = pos * (px - entry) / entry
            if ret <= (-0.015 / leverage) or ret >= (0.03 / leverage) or (pos == 1 and px < ll) or (pos == -1 and px > hh):
                pnl = ret * notional
                capital += pnl
                capital -= notional * TRADE_COST
                trades[-1].update({"exit": px, "exit_i": i, "pnl": pnl})
                pos = 0; entry = 0.0; notional = 0.0
    return summarize("20-bar Breakout", rows, equity_curve, trades, capital)


def summarize(name, rows, equity_curve, trades, final_capital):
    closed = [t for t in trades if 'pnl' in t]
    if not equity_curve:
        equity_curve = [INITIAL_CAPITAL]
    peak = equity_curve[0]
    max_dd = 0.0
    for e in equity_curve:
        peak = max(peak, e)
        max_dd = max(max_dd, (peak - e) / peak if peak else 0)
    gross = final_capital - INITIAL_CAPITAL
    wins = [t for t in closed if t['pnl'] > 0]
    return {
        "strategy": name,
        "trades": len(closed),
        "win_rate": round(100*len(wins)/len(closed),1) if closed else 0,
        "pnl": round(gross,2),
        "final": round(final_capital,2),
        "max_dd_pct": round(100*max_dd,1),
    }


def analyze_altrbtc_ratio(pair, btc_rows):
    """Analyze ALT/BTC ratio trend — the VirtualBacon truth"""
    if not btc_rows:
        return None
    
    btc_closes = [r['close'] for r in btc_rows]
    
    # Simple analysis: current ratio trend
    if len(btc_closes) < 50:
        return None
    
    # 20-period SMA of the ratio
    sma20 = sma(btc_closes, 20)
    sma50 = sma(btc_closes, 50)
    
    current = btc_closes[-1]
    high_20 = max(btc_closes[-20:])
    low_20 = min(btc_closes[-20:])
    
    # Position in recent range
    if high_20 != low_20:
        range_position = (current - low_20) / (high_20 - low_20)
    else:
        range_position = 0.5
    
    # Trend
    trend = "UP" if sma20[-1] > sma50[-1] else "DOWN"
    
    return {
        "pair": pair,
        "current_ratio": round(current, 8),
        "trend": trend,
        "range_position": round(range_position * 100, 1),
        "sma20": round(sma20[-1], 8),
        "sma50": round(sma50[-1], 8),
    }


def run():
    print("=" * 60)
    print("BINANCE BACKTESTER v2 — VirtualBacon Integration")
    print("=" * 60)
    
    # 1. Run backtests on all pairs
    print("\n📊 PHASE 1: Backtesting all pairs (USD)")
    print("-" * 40)
    
    full_report = {}
    for pair in ALL_PAIRS:
        print(f"\n🔍 {pair}...")
        rows = fetch_klines(pair, INTERVAL, LIMIT)
        if not rows or len(rows) < 100:
            print(f"  ⚠ Insufficient data for {pair}")
            continue
        
        full_report[pair] = [
            backtest_trend(rows),
            backtest_meanrev(rows),
            backtest_breakout(rows),
        ]
        print(f"  ✅ Done ({len(rows)} candles)")
        time.sleep(0.5)  # Rate limit respect
    
    # 2. ALT/BTC ratio analysis
    print("\n\n📈 PHASE 2: ALT/BTC Ratio Analysis (VirtualBacon)")
    print("-" * 40)
    
    altrbtc_report = {}
    for pair in ALTBTC_PAIRS:
        print(f"\n🔍 {pair}...")
        rows = fetch_klines(pair, INTERVAL, LIMIT)
        if not rows:
            print(f"  ⚠ No data for {pair}")
            continue
        
        result = analyze_altrbtc_ratio(pair, rows)
        if result:
            altrbtc_report[pair] = result
            print(f"  📊 Trend: {result['trend']} | Range: {result['range_position']}%")
        time.sleep(0.5)
    
    # 3. Print results
    print("\n\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    # USD backtests
    print("\n💰 USD BACKTESTS ($5,000 initial, 2x leverage)")
    print("-" * 60)
    
    for pair, strategies in full_report.items():
        print(f"\n📌 {pair}")
        print(f"  {'Strategy':<25} {'Trades':>6} {'Win%':>6} {'PnL':>10} {'MaxDD':>6}")
        print(f"  {'-'*55}")
        for s in strategies:
            print(f"  {s['strategy']:<25} {s['trades']:>6} {s['win_rate']:>5.1f}% ${s['pnl']:>9.2f} {s['max_dd_pct']:>5.1f}%")
    
    # ALT/BTC ratios
    print("\n\n📈 ALT/BTC RATIO ANALYSIS")
    print("-" * 60)
    print(f"  {'Pair':<12} {'Ratio':>12} {'Trend':>6} {'Range%':>8}")
    print(f"  {'-'*40}")
    for pair, data in altrbtc_report.items():
        print(f"  {pair:<12} {data['current_ratio']:>12.8f} {data['trend']:>6} {data['range_position']:>7.1f}%")
    
    # 4. Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    # Best strategy per pair
    print("\n🏆 Best strategy per pair:")
    for pair, strategies in full_report.items():
        best = max(strategies, key=lambda x: x['pnl'])
        print(f"  {pair}: {best['strategy']} → ${best['pnl']:.2f}")
    
    # Overall
    all_pnls = [s['pnl'] for strats in full_report.values() for s in strats]
    avg_pnl = sum(all_pnls) / len(all_pnls) if all_pnls else 0
    total_pnl = sum(all_pnls)
    
    print(f"\n📊 Total PnL across all: ${total_pnl:.2f}")
    print(f"📊 Average PnL per strategy: ${avg_pnl:.2f}")
    
    # VirtualBacon alignment
    print("\n🎯 VirtualBacon Alignment:")
    print(f"  S Tier pairs tested: {[p for p in S_TIER if p in full_report]}")
    print(f"  A Tier pairs tested: {[p for p in A_TIER if p in full_report]}")
    
    # ALT/BTC signals
    buy_signals = [p for p, d in altrbtc_report.items() if d['trend'] == 'DOWN' and d['range_position'] < 30]
    if buy_signals:
        print(f"\n🟢 ALT/BTC BUY SIGNALS (near support): {buy_signals}")
    else:
        print(f"\n🔴 No ALT/BTC buy signals right now")
    
    print("\n" + "=" * 60)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    run()
