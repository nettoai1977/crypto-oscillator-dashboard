#!/usr/bin/env python3
"""
Daily Crypto Signal Scanner
Checks ALT/BTC ratios, entry/exit zones, and sector correlation.
Outputs a report suitable for Telegram notification.
"""
import requests
import json
from datetime import datetime

# Portfolio coins from trading plan
PORTFOLIO = {
    # Core (60%)
    "FETUSDT": {"tier": "S", "alloc": "25%", "entry_low": 0.1564, "entry_high": 0.1720, "stop": 0.1500},
    "SOLUSDT": {"tier": "A", "alloc": "20%", "entry_low": 74.50, "entry_high": 81.95, "stop": 70.00},
    "RENDERUSDT": {"tier": "S", "alloc": "15%", "entry_low": 1.456, "entry_high": 1.602, "stop": 1.40},
    # Tactical (25%)
    "XRPUSDT": {"tier": "A", "alloc": "15%", "entry_low": 1.084, "entry_high": 1.192, "stop": 1.00},
    "BNBUSDT": {"tier": "A", "alloc": "10%", "entry_low": 566.25, "entry_high": 622.88, "stop": 540.00},
    # Speculative (15%)
    "ONDOUSDT": {"tier": "SPEC", "alloc": "10%", "entry_low": 0.30, "entry_high": 0.38, "stop": 0.25},
    "INJUSDT": {"tier": "SPEC", "alloc": "5%", "entry_low": 0.0, "entry_high": 999999, "stop": 0.0},
}

# ALT/BTC pairs to monitor
ALTBTC_PAIRS = ["ETHBTC", "SOLBTC", "XRPBTC", "BNBBTC", "TRXBTC", "FETBTC", "RENDERBTC"]

# Sector tokens for correlation tracking
SECTORS = {
    "AI": ["FETUSDT", "RENDERUSDT", "TAOUSDT", "AKTUSDT", "VIRTUALUSDT"],
    "RWA": ["ONDOUSDT", "CPOOLUSDT", "MPLUSDT"],
    "L1": ["SOLUSDT", "ETHUSDT", "AVAXUSDT", "NEARUSDT"],
    "MEME": ["DOGEUSDT", "SHIBUSDT", "PEPEUSDT", "WIFUSDT", "FLOKIUSDT"],
}


def fetch_price(symbol):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=10)
        data = r.json()
        return {
            "price": float(data["lastPrice"]),
            "change_24h": float(data["priceChangePercent"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
            "volume": float(data["quoteVolume"]),
        }
    except:
        return None


def fetch_klines(symbol, interval="1h", limit=100):
    try:
        r = requests.get(
            f"https://api.binance.com/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            timeout=10,
        )
        return [float(k[4]) for k in r.json()]
    except:
        return []


def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
        if len(gains) > period:
            gains.pop(0)
            losses.pop(0)
    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    rs = avg_gain / avg_loss if avg_loss else 999
    return 100 - 100 / (1 + rs)


def check_entry_exit(coin, data, info):
    """Check if coin is in entry or exit zone"""
    price = data["price"]
    signals = []

    if price <= info["entry_high"] and price >= info["entry_low"]:
        signals.append("🟢 IN ENTRY ZONE")
    elif price < info["entry_low"]:
        signals.append("🟢 BELOW ENTRY ZONE — aggressive buy")
    elif price > info["entry_high"] * 1.20:
        signals.append("🔴 ABOVE 20% OF ENTRY — consider taking profit")

    if info["stop"] > 0 and price <= info["stop"]:
        signals.append("⚠️ STOP LOSS HIT")

    rsi = calc_rsi(fetch_klines(coin))
    if rsi < 30:
        signals.append(f"🟢 RSI OVERSOLD ({rsi:.1f})")
    elif rsi > 70:
        signals.append(f"🔴 RSI OVERBOUGHT ({rsi:.1f})")

    return signals, rsi


def check_sector_correlation(sector_name, pairs):
    """Check if sector tokens are moving together"""
    changes = []
    for pair in pairs:
        data = fetch_price(pair)
        if data:
            changes.append((pair, data["change_24h"]))

    if len(changes) < 2:
        return None

    avg_change = sum(c for _, c in changes) / len(changes)
    all_same_direction = all(c > 0 for _, c in changes) or all(c < 0 for _, c in changes)

    if all_same_direction and abs(avg_change) > 2:
        return {
            "sector": sector_name,
            "avg_change": avg_change,
            "direction": "UP" if avg_change > 0 else "DOWN",
            "tokens": changes,
            "correlated": True,
        }
    return {
        "sector": sector_name,
        "avg_change": avg_change,
        "direction": "MIXED",
        "tokens": changes,
        "correlated": False,
    }


def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = []
    report.append(f"📊 DAILY CRYPTO SIGNALS — {now}")
    report.append("=" * 40)

    # 1. Portfolio status
    report.append("\n💰 PORTFOLIO STATUS")
    report.append("-" * 40)

    for coin, info in PORTFOLIO.items():
        data = fetch_price(coin)
        if not data:
            continue

        signals, rsi = check_entry_exit(coin, data, info)

        report.append(f"\n{coin} ({info['tier']} Tier — {info['alloc']})")
        report.append(f"  Price: ${data['price']:,.6f} ({data['change_24h']:+.1f}%)")
        report.append(f"  24h Range: ${data['low_24h']:,.6f} — ${data['high_24h']:,.6f}")
        report.append(f"  RSI: {rsi:.1f}")
        report.append(f"  Entry Zone: ${info['entry_low']:,.6f} — ${info['entry_high']:,.6f}")

        for s in signals:
            report.append(f"  {s}")

    # 2. ALT/BTC ratios
    report.append("\n\n📈 ALT/BTC RATIOS")
    report.append("-" * 40)

    for pair in ALTBTC_PAIRS:
        data = fetch_price(pair)
        if data:
            trend = "🟢" if data["change_24h"] > 0 else "🔴"
            report.append(f"  {trend} {pair}: {data['price']:.8f} ({data['change_24h']:+.1f}%)")

    # 3. Sector correlation
    report.append("\n\n🔗 SECTOR CORRELATION (24h)")
    report.append("-" * 40)

    for sector_name, tokens in SECTORS.items():
        result = check_sector_correlation(sector_name, tokens)
        if result:
            icon = "🟢" if result["correlated"] else "⚪"
            report.append(f"  {icon} {result['sector']}: {result['avg_change']:+.1f}% avg — {result['direction']}")
            if result["correlated"]:
                report.append(f"     ⚡ CORRELATED MOVE — narrative signal!")
                for token, change in result["tokens"]:
                    report.append(f"       {token}: {change:+.1f}%")

    # 4. Summary
    report.append("\n\n" + "=" * 40)
    report.append("📋 SUMMARY")
    report.append("=" * 40)

    # Count signals
    entry_count = 0
    profit_count = 0
    for coin, info in PORTFOLIO.items():
        data = fetch_price(coin)
        if data:
            if data["price"] <= info["entry_high"]:
                entry_count += 1
            if info["stop"] > 0 and data["price"] <= info["stop"]:
                profit_count += 1

    report.append(f"  Coins in entry zone: {entry_count}/{len(PORTFOLIO)}")
    report.append(f"  Coins at stop loss: {profit_count}/{len(PORTFOLIO)}")

    if entry_count > 3:
        report.append("  ⚠️ Many coins at support — market-wide dip. DCA opportunity.")
    elif entry_count == 0:
        report.append("  📈 No coins at entry — wait for pullback.")

    report.append(f"\n⏰ Next scan: Tomorrow")
    report.append("💡 Reply /signals to get this daily")

    return "\n".join(report)


if __name__ == "__main__":
    print(run())
