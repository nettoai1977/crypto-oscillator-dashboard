#!/usr/bin/env python3
import math, statistics, requests, json
from datetime import datetime

PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "1h"
LIMIT = 1000
INITIAL_CAPITAL = 5000.0
FEE = 0.0004  # 4 bps per side rough futures maker/taker blended estimate
SLIPPAGE = 0.0002
TRADE_COST = FEE + SLIPPAGE


def fetch_klines(symbol, interval="1h", limit=1000):
    url = "https://api.binance.com/api/v3/klines"
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
    pos = 0  # 1 long, -1 short, 0 flat
    entry = 0.0
    notional = 0.0
    equity_curve = []
    trades = []
    for i in range(50, len(rows)):
        px = closes[i]
        prev_px = closes[i-1]
        signal = 1 if e12[i] > e48[i] else -1 if e12[i] < e48[i] else 0

        # mark to market
        unreal = 0.0
        if pos != 0:
            unreal = pos * (px - entry) / entry * notional
        equity_curve.append(capital + unreal)

        if pos == 0 and signal != 0:
            pos = signal
            notional = capital * risk_frac * leverage
            capital -= notional * TRADE_COST
            entry = px
            trades.append({"side": "LONG" if pos==1 else "SHORT", "entry": entry, "entry_i": i})
        elif pos != 0:
            # trend flip or 2% stop or 3.5% take profit on leveraged notional
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
    pos = 0
    entry = 0.0
    notional = 0.0
    equity_curve = []
    trades = []
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
    pos = 0
    entry = 0.0
    notional = 0.0
    equity_curve = []
    trades = []
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
    avg_daily = gross / max(1, len(rows)/24)
    return {
        "strategy": name,
        "trades": len(closed),
        "win_rate": round(100*len(wins)/len(closed),1) if closed else 0,
        "pnl": round(gross,2),
        "final": round(final_capital,2),
        "avg_daily": round(avg_daily,2),
        "max_dd_pct": round(100*max_dd,1),
    }


def run():
    report = {}
    for pair in PAIRS:
        rows = fetch_klines(pair, INTERVAL, LIMIT)
        report[pair] = [
            backtest_trend(rows),
            backtest_meanrev(rows),
            backtest_breakout(rows),
        ]
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    run()
