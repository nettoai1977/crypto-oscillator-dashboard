#!/usr/bin/env python3
"""
DCA Bot Strategy —改良版 (Improved from Mastering Assets concept)
Adds Dollar-Cost Averaging bot strategy with proper risk management.
"""
import requests
import json
from datetime import datetime

INITIAL_CAPITAL = 5000.0
FEE = 0.001  # 10 bps (taker fee)


def fetch_klines(symbol, interval="1d", limit=365):
    try:
        r = requests.get(
            f"https://api.binance.com/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            timeout=30,
        )
        data = r.json()
        return [{"close": float(k[4]), "low": float(k[3]), "high": float(k[2])} for k in data]
    except Exception as e:
        print(f"  ⚠ Failed to fetch {symbol}: {e}")
        return []


def backtest_dca(rows, base_amount=50, multiplier=1.5, take_profit_pct=0.03, max_positions=10):
    """
    DCA Bot Strategy (改良版)
    
    Based on Mastering Assets' 1-3-7 ladder concept but with SAFETY improvements:
    
    Core concept: Buy more as price drops, sell on bounce
    Safety: Hard stop loss, max positions limit, take profit targets
    
    Parameters:
    - base_amount: Initial buy size in USDT
    - multiplier: How much to increase each DCA level (1.5x = conservative)
    - take_profit_pct: Target profit % to close all positions
    - max_positions: Maximum DCA buys before forced exit (risk management!)
    """
    capital = INITIAL_CAPITAL
    positions = []  # List of {price, amount, qty}
    total_invested = 0
    trades = []
    
    for i, row in enumerate(rows):
        price = row["close"]
        low = row["low"]
        
        # Check if we should DCA buy (price dropped from last buy or from start)
        should_buy = False
        if len(positions) == 0:
            should_buy = True
        elif price < positions[-1]["price"] * 0.97:  # 3% drop from last buy
            should_buy = True
        
        # Execute DCA buy
        if should_buy and len(positions) < max_positions and capital >= base_amount:
            # Calculate position size (1-3-7 ladder style)
            level = len(positions)
            if level == 0:
                amount = base_amount
            elif level < 3:
                amount = base_amount * multiplier
            else:
                amount = base_amount * (multiplier ** 2)  # More aggressive at deeper levels
            
            amount = min(amount, capital * 0.25)  # Never more than 25% of capital per buy
            qty = amount / price
            cost = amount * (1 + FEE)
            
            if cost <= capital:
                capital -= cost
                total_invested += amount
                positions.append({"price": price, "amount": amount, "qty": qty, "level": level})
                trades.append({"type": "BUY", "price": price, "amount": amount, "level": level, "day": i})
        
        # Check take profit (average price vs current)
        if len(positions) >= 2:
            avg_price = sum(p["price"] * p["qty"] for p in positions) / sum(p["qty"] for p in positions)
            total_qty = sum(p["qty"] for p in positions)
            current_value = total_qty * price
            invested_value = sum(p["amount"] for p in positions)
            pnl_pct = (current_value - invested_value) / invested_value if invested_value > 0 else 0
            
            if pnl_pct >= take_profit_pct:
                # Take profit
                profit = current_value - invested_value
                capital += current_value * (1 - FEE)
                trades.append({
                    "type": "SELL_TP", "price": price, "pnl": profit,
                    "pnl_pct": pnl_pct, "positions": len(positions), "day": i
                })
                total_invested = 0
                positions = []
        
        # HARD STOP LOSS — if price drops 15% below average, exit everything
        if len(positions) >= 2:
            avg_price = sum(p["price"] * p["qty"] for p in positions) / sum(p["qty"] for p in positions)
            if price < avg_price * 0.85:
                total_qty = sum(p["qty"] for p in positions)
                current_value = total_qty * price
                invested_value = sum(p["amount"] for p in positions)
                loss = current_value - invested_value
                capital += current_value * (1 - FEE)
                trades.append({
                    "type": "SELL_SL", "price": price, "pnl": loss,
                    "pnl_pct": loss / invested_value if invested_value > 0 else 0,
                    "positions": len(positions), "day": i
                })
                total_invested = 0
                positions = []
    
    # Close any remaining positions at last price
    if positions:
        last_price = rows[-1]["close"]
        total_qty = sum(p["qty"] for p in positions)
        current_value = total_qty * last_price
        invested_value = sum(p["amount"] for p in positions)
        capital += current_value * (1 - FEE)
        trades.append({
            "type": "SELL_CLOSE", "price": last_price,
            "pnl": current_value - invested_value,
            "positions": len(positions), "day": len(rows) - 1
        })
    
    return summarize("DCA Bot (改良版)", trades, capital)


def backtest_dca_conservative(rows, base_amount=50):
    """Conservative DCA — fixed amount, no multiplier, strict stops"""
    return backtest_dca(rows, base_amount=base_amount, multiplier=1.0, take_profit_pct=0.02, max_positions=5)


def backtest_dca_aggressive(rows, base_amount=50):
    """Aggressive DCA — larger multiplier, higher take profit target"""
    return backtest_dca(rows, base_amount=base_amount, multiplier=2.0, take_profit_pct=0.05, max_positions=15)


def summarize(name, trades, final_capital):
    sells = [t for t in trades if t["type"].startswith("SELL")]
    wins = [t for t in sells if t["pnl"] > 0]
    total_pnl = sum(t["pnl"] for t in sells)
    
    return {
        "strategy": name,
        "total_trades": len(trades),
        "buys": len([t for t in trades if t["type"] == "BUY"]),
        "sells": len(sells),
        "win_rate": round(100 * len(wins) / len(sells), 1) if sells else 0,
        "pnl": round(total_pnl, 2),
        "final_capital": round(final_capital, 2),
        "return_pct": round((final_capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100, 2),
    }


def run():
    # Test on the same pairs as our main backtest
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "FETUSDT", "BNBUSDT", "ONDOUSDT"]
    
    print("=" * 70)
    print("DCA BOT STRATEGY — 改良版 (Improved from Mastering Assets)")
    print("=" * 70)
    print("Key improvements over standard Martingale DCA:")
    print("  ✅ Hard stop loss at 15% below average")
    print("  ✅ Max position limit (prevents unlimited averaging)")
    print("  ✅ Position sizing caps (never more than 25% per buy)")
    print("  ✅ Conservative, Balanced, and Aggressive variants")
    print("=" * 70)
    
    all_results = {}
    
    for pair in pairs:
        print(f"\n🔍 {pair} (365 daily candles)...")
        rows = fetch_klines(pair, "1d", 365)
        if not rows or len(rows) < 30:
            print(f"  ⚠ Insufficient data")
            continue
        
        conservative = backtest_dca_conservative(rows)
        balanced = backtest_dca(rows)
        aggressive = backtest_dca_aggressive(rows)
        
        all_results[pair] = [conservative, balanced, aggressive]
        
        print(f"  Conservative: ${conservative['pnl']:+.2f} ({conservative['return_pct']:+.1f}%) | WR: {conservative['win_rate']}% | {conservative['sells']} sells")
        print(f"  Balanced:     ${balanced['pnl']:+.2f} ({balanced['return_pct']:+.1f}%) | WR: {balanced['win_rate']}% | {balanced['sells']} sells")
        print(f"  Aggressive:   ${aggressive['pnl']:+.2f} ({aggressive['return_pct']:+.1f}%) | WR: {aggressive['win_rate']}% | {aggressive['sells']} sells")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY — Best DCA variant per pair")
    print("=" * 70)
    
    for pair, strategies in all_results.items():
        best = max(strategies, key=lambda x: x["pnl"])
        print(f"  {pair}: {best['strategy']} → ${best['pnl']:+.2f} ({best['return_pct']:+.1f}%)")
    
    # Cross-comparison with our Mean Reversion strategy
    print("\n" + "=" * 70)
    print("DCA vs MEAN REVERSION (from main backtest)")
    print("=" * 70)
    print("  DCA works best in: Sideways/ranging markets")
    print("  Mean Rev works best in: Oversold bounces")
    print("  DCA weakness: Sustained downtrends (even with stop loss)")
    print("  Mean Rev weakness: Trending markets (misses the move)")
    print("\n  💡 RECOMMENDATION: Use both in different market conditions")
    print("  - Sideways market → DCA bots")
    print("  - Oversold bounce → Mean Reversion entries")
    print("  - Uptrend → Trend following")
    
    return all_results


if __name__ == "__main__":
    run()
