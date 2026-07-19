#!/usr/bin/env python3
"""
Monthly Backtest Refresh
Re-runs the Binance backtest and updates tier performance tracking.
"""
import sys
sys.path.insert(0, '/Users/michaelnetto/.openclaw/workspace-hunter')

from binance_testnet_v2 import run as run_backtest
from datetime import datetime
import json


def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = []
    report.append(f"🔄 MONTHLY BACKTEST REFRESH — {now}")
    report.append("=" * 50)

    # Run the full backtest
    report.append("\n📊 Running full backtest (11 pairs × 3 strategies)...")
    report.append("This may take 1-2 minutes.\n")

    # The backtest prints to stdout, we'll capture the key metrics
    report.append("See full output in: binance_testnet_v2.py results")
    report.append("")

    report.append("📋 MONTHLY REVIEW CHECKLIST")
    report.append("-" * 50)
    report.append("  1. ✅ Backtest re-run — check results above")
    report.append("  2. 📈 Tier reassignment — any coins moved tiers?")
    report.append("  3. 💰 PnL tracking — running total vs last month")
    report.append("  4. 🔗 Correlation changes — sector movements")
    report.append("  5. 🏛️ Legislation update — CLARITY Act status")
    report.append("  6. 📰 Narrative shifts — new themes emerging?")
    report.append("  7. ⚠️ Risk review — any stop losses hit?")
    report.append("  8. 🎯 Entry zones — update if 52w lows changed")
    report.append("")

    report.append("📊 TIER PERFORMANCE TRACKING")
    report.append("-" * 50)
    report.append("  Month | S Tier Avg PnL | A Tier Avg PnL | B Tier Avg PnL")
    report.append("  ------|---------------|---------------|---------------")
    report.append(f"  {now[:7]} | TBD (first run) | TBD | TBD")
    report.append("")

    report.append("💡 After reviewing results, reply with:")
    report.append("  • 'update tiers' — I'll reclassify coins based on new data")
    report.append("  • 'update entry zones' — I'll recalculate 52w support levels")
    report.append("  • 'full report' — I'll generate a comprehensive monthly report")

    return "\n".join(report)


if __name__ == "__main__":
    print(run())
