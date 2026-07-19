#!/usr/bin/env python3
"""
TBO-Style Trend Indicator (Inspired by Aaron Dishner's TBO)
Implements cloud-based trend detection with multi-timeframe support.
"""
import math
import requests
import json
from datetime import datetime

BINANCE_API = "https://api.binance.com/api/v3"


def fetch_klines(symbol, interval="1d", limit=200):
    try:
        r = requests.get(
            f"{BINANCE_API}/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            timeout=30,
        )
        data = r.json()
        return [
            {
                "time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            }
            for k in data
        ]
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
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


def calc_tbo(rows, fast_period=20, slow_period=50):
    """
    TBO-Style Indicator:
    - Fast line: EMA of (high+low)/2
    - Slow line: EMA of fast line (smoothed)
    - Cloud: area between fast and slow
    - Signal: price vs cloud position
    - Trend: fast line vs slow line direction
    """
    closes = [r["close"] for r in rows]
    highs = [r["high"] for r in rows]
    lows = [r["low"] for r in rows]
    mids = [(h + l) / 2 for h, l in zip(highs, lows)]

    fast = ema(mids, fast_period)
    slow = ema(fast, slow_period)

    # Support/resistance levels (adaptive)
    supports = []
    for i in range(len(rows)):
        if i < slow_period:
            supports.append(0)
            continue
        lookback = min(20, i)
        recent_lows = lows[i - lookback : i]
        supports.append(min(recent_lows) * 1.02)  # 2% above recent low

    # Generate signals
    signals = []
    for i in range(len(rows)):
        px = closes[i]
        f = fast[i]
        s = slow[i]

        # Cloud position
        if px > max(f, s):
            cloud_status = "ABOVE_CLOUD"
        elif px < min(f, s):
            cloud_status = "BELOW_CLOUD"
        else:
            cloud_status = "IN_CLOUD"

        # Trend direction
        if f > s:
            trend = "BULLISH"
        else:
            trend = "BEARISH"

        # Signal strength
        if cloud_status == "ABOVE_CLOUD" and trend == "BULLISH":
            signal = "STRONG_BULLISH"
        elif cloud_status == "BELOW_CLOUD" and trend == "BEARISH":
            signal = "STRONG_BEARISH"
        elif cloud_status == "ABOVE_CLOUD" and trend == "BEARISH":
            signal = "WEAK_BULLISH"
        else:
            signal = "WEAK_BEARISH"

        # Price vs fast line (overextended check)
        if f > 0:
            deviation = (px - f) / f * 100
        else:
            deviation = 0

        signals.append({
            "signal": signal,
            "cloud_status": cloud_status,
            "trend": trend,
            "fast": f,
            "slow": s,
            "deviation": deviation,
            "support": supports[i],
        })

    return fast, slow, signals


def analyze_multi_timeframe(symbol, intervals=None):
    """Analyze across multiple timeframes"""
    if intervals is None:
        intervals = [
            ("1w", "Weekly"),
            ("1d", "Daily"),
            ("4h", "4-Hour"),
            ("1h", "1-Hour"),
        ]

    results = []
    for interval, label in intervals:
        limit = 200 if interval in ["1d", "4h", "1h"] else 100
        rows = fetch_klines(symbol, interval, limit)
        if not rows:
            continue

        fast, slow, signals = calc_tbo(rows)
        last = signals[-1]
        prev = signals[-2] if len(signals) > 1 else last

        results.append({
            "timeframe": label,
            "interval": interval,
            "price": rows[-1]["close"],
            "fast_line": round(last["fast"], 6),
            "slow_line": round(last["slow"], 6),
            "signal": last["signal"],
            "trend": last["trend"],
            "cloud_status": last["cloud_status"],
            "deviation": round(last["deviation"], 2),
            "support": round(last["support"], 6),
            "trend_changed": prev["trend"] != last["trend"],
        })

    return results


def format_signal(signal):
    icons = {
        "STRONG_BULLISH": "🟢🟢 STRONG BULLISH",
        "WEAK_BULLISH": "🟢 WEAK BULLISH",
        "STRONG_BEARISH": "🔴🔴 STRONG BEARISH",
        "WEAK_BEARISH": "🔴 WEAK BEARISH",
    }
    return icons.get(signal, "⚪ UNKNOWN")


def run():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "FETUSDT", "XRPUSDT", "BNBUSDT"]

    print("=" * 70)
    print("TBO-STYLE TREND INDICATOR — Multi-Timeframe Analysis")
    print("Inspired by Aaron Dishner's TBO (Trending Breakout)")
    print("=" * 70)

    for symbol in symbols:
        print(f"\n{'─' * 70}")
        print(f"📊 {symbol}")
        print(f"{'─' * 70}")

        results = analyze_multi_timeframe(symbol)

        if not results:
            print("  No data available")
            continue

        # Overall verdict
        bullish_count = sum(1 for r in results if "BULLISH" in r["signal"])
        bearish_count = sum(1 for r in results if "BEARISH" in r["signal"])

        print(f"\n  {'Timeframe':<12} {'Price':>12} {'Fast':>12} {'Slow':>12} {'Signal':<20} {'Dev%':>6}")
        print(f"  {'─' * 72}")

        for r in results:
            sig = format_signal(r["signal"])
            print(
                f"  {r['timeframe']:<12} ${r['price']:>11,.4f} "
                f"${r['fast_line']:>11,.4f} ${r['slow_line']:>11,.4f} "
                f"{sig:<20} {r['deviation']:>+5.1f}%"
            )
            if r["trend_changed"]:
                print(f"    ⚡ TREND CHANGE on {r['timeframe']}!")

        # Verdict
        if bullish_count > bearish_count:
            verdict = "🟢 BULLISH — more timeframes agree"
        elif bearish_count > bullish_count:
            verdict = "🔴 BEARISH — more timeframes agree"
        else:
            verdict = "⚪ MIXED — conflicting signals"

        print(f"\n  VERDICT: {verdict}")
        print(f"  Support: ${results[-1]['support']:,.4f}")
        print(f"  Deviation from fast line: {results[-1]['deviation']:+.1f}%")
        if abs(results[-1]["deviation"]) > 15:
            print(f"  ⚠️ OVEREXTENDED — watch for mean reversion")

    print(f"\n{'=' * 70}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    run()
