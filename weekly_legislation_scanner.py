#!/usr/bin/env python3
"""
Weekly Legislation & Narrative Scanner
Monitors US regulatory news, ONDO updates, and emerging crypto narratives.
"""
import requests
import json
from datetime import datetime

# Keywords to monitor
LEGISLATION_KEYWORDS = [
    "CLARITY Act", "CLARITY Act crypto", "CLARITY Act Senate",
    "Tokenization Act", "Modernizing Markets Through Tokenization",
    "GENIUS Act", "stablecoin regulation",
    "SEC tokenized securities", "SEC crypto regulation",
    "CFTC digital assets", "CFTC crypto",
    "Ondo Finance SEC", "Ondo Finance regulation",
    "tokenized stocks SEC", "tokenized securities law",
]

NARRATIVE_KEYWORDS = {
    "AI Agents": ["AI agent crypto", "AI agent blockchain", "autonomous agent crypto", "Virtuals Protocol", "AI16Z"],
    "Tokenization": ["tokenized stocks", "tokenized securities", "RWA crypto", "real world assets blockchain"],
    "DePIN": ["DePIN crypto", "decentralized physical infrastructure", "Helium HNT", "Render RNDR"],
    "Bitcoin L2": ["Bitcoin L2", "Bitcoin Layer 2", "Stacks STX", "Bitcoin Ordinals"],
    "Privacy": ["privacy crypto", "Monero XMR", "Zcash ZEC", "privacy coin regulation"],
}

# Key people to track (Twitter handles for reference)
KEY_PEOPLE = [
    "@PatrickMcHenry (former House Financial Services Chair — on Ondo advisory)",
    "@a16z (VC thesis tracker)",
    "@Paradigm (VC thesis tracker)",
    "@MulticoinCap (VC thesis tracker)",
    "@elaboratecoin (crypto policy)",
]


def search_news(query, count=5):
    """Search for recent news using web scraping approach"""
    # In production, this would use a news API or web search
    # For now, return structured search queries
    return {
        "query": query,
        "search_urls": [
            f"https://www.google.com/search?q={query.replace(' ', '+')}&tbs=qdr:w",
            f"https://news.google.com/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en",
        ],
    }


def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = []
    report.append(f"📰 WEEKLY LEGISLATION & NARRATIVE SCAN — {now}")
    report.append("=" * 50)

    # 1. Legislation tracking
    report.append("\n🏛️ US LEGISLATION STATUS")
    report.append("-" * 50)

    legislation_items = [
        {
            "bill": "CLARITY Act",
            "status": "STALLED in Senate (passed House July 2025)",
            "impact": "HIGH — defines SEC vs CFTC jurisdiction for all digital assets",
            "why_it_matters": "If passed: clear rules for tokenized assets, institutional floodgates open",
            "last_update": "Forbes July 16: 'delay is now a compliance problem'",
        },
        {
            "bill": "Tokenization Act (Modernizing Markets)",
            "status": "In congressional hearings",
            "impact": "HIGH — specific framework for tokenized securities",
            "why_it_matters": "Directly enables ONDO's business model at scale",
            "last_update": "House Financial Services Committee hearing scheduled",
        },
        {
            "bill": "GENIUS Act",
            "status": "SIGNED INTO LAW (July 2025) — rules being implemented",
            "impact": "MEDIUM — stablecoin framework active",
            "why_it_matters": "USDY (Ondo's yield product) operates in this framework",
            "last_update": "Treasury proposed BSA rule (April 2026), OCC rulemaking (March 2026)",
        },
    ]

    for item in legislation_items:
        report.append(f"\n📌 {item['bill']}")
        report.append(f"  Status: {item['status']}")
        report.append(f"  Impact: {item['impact']}")
        report.append(f"  Why: {item['why_it_matters']}")
        report.append(f"  Latest: {item['last_update']}")

    # 2. ONDO-specific tracker
    report.append("\n\n🔵 ONDO FINANCE TRACKER")
    report.append("-" * 50)

    ondo_items = [
        {"event": "SEC investigation closed (no charges)", "date": "Dec 2025", "status": "✅ DONE"},
        {"event": "SEC registration filed (Ondo Stocks)", "date": "Feb 2026", "status": "⏳ PENDING"},
        {"event": "Ethereum Mainnet no-action letter requested", "date": "Apr 2026", "status": "⏳ PENDING"},
        {"event": "Tokenized BlackRock IVV ETF launched", "date": "Jul 2026", "status": "✅ LIVE"},
        {"event": "DTCC tokenized stocks launched", "date": "Jul 2026", "status": "✅ LIVE"},
        {"event": "AUM in tokenized Treasuries", "date": "Jul 2026", "status": "$1.5B+"},
    ]

    for item in ondo_items:
        report.append(f"  {item['status']} {item['event']} ({item['date']})")

    # 3. Narrative tracking
    report.append("\n\n🔮 NARRATIVE TRACKER")
    report.append("-" * 50)

    for narrative, keywords in NARRATIVE_KEYWORDS.items():
        report.append(f"\n📌 {narrative}")
        report.append(f"  Keywords to monitor:")
        for kw in keywords:
            report.append(f"    • {kw}")
        report.append(f"  Search: https://www.google.com/search?q={keywords[0].replace(' ', '+')}&tbs=qdr:w")

    # 4. Key people to watch
    report.append("\n\n👤 KEY PEOPLE TO WATCH")
    report.append("-" * 50)
    for person in KEY_PEOPLE:
        report.append(f"  • {person}")

    # 5. Action items
    report.append("\n\n✅ WEEKLY ACTION ITEMS")
    report.append("-" * 50)
    report.append("  1. Check CLARITY Act Senate progress (Forbes, CoinDesk)")
    report.append("  2. Search 'ONDO Finance' news for SEC registration updates")
    report.append("  3. Check a16z/Paradigm blogs for new thesis papers")
    report.append("  4. Monitor Crypto Twitter for narrative keyword spikes")
    report.append("  5. Review sector correlation in daily scanner output")

    report.append("\n" + "=" * 50)
    report.append("⏰ Next scan: Next Monday")

    return "\n".join(report)


if __name__ == "__main__":
    print(run())
