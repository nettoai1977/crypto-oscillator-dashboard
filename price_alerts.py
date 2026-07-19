#!/usr/bin/env python3
"""
Real-Time Price Alert System
Monitors Binance WebSocket for price movements and sends Telegram alerts.
"""
import websocket
import json
import time
import requests
from datetime import datetime

# Portfolio alert configuration
ALERTS = {
    "FETUSDT": {"coin": "FET", "tier": "S", "entry_low": 0.1564, "entry_high": 0.1720, "stop": 0.1500, "tp": 0.20},
    "SOLUSDT": {"coin": "SOL", "tier": "A", "entry_low": 74.50, "entry_high": 81.95, "stop": 70.00, "tp": 95.00},
    "RENDERUSDT": {"coin": "RENDER", "tier": "S", "entry_low": 1.456, "entry_high": 1.602, "stop": 1.40, "tp": 2.00},
    "XRPUSDT": {"coin": "XRP", "tier": "A", "entry_low": 1.084, "entry_high": 1.192, "stop": 1.00, "tp": 1.50},
    "BNBUSDT": {"coin": "BNB", "tier": "A", "entry_low": 566.25, "entry_high": 622.88, "stop": 540.00, "tp": 700.00},
    "ONDOUSDT": {"coin": "ONDO", "tier": "SPEC", "entry_low": 0.30, "entry_high": 0.38, "stop": 0.25, "tp": 0.60},
    "INJUSDT": {"coin": "INJ", "tier": "SPEC", "entry_low": 0, "entry_high": 999999, "stop": 0, "tp": 10.00},
}

# Telegram config
TELEGRAM_TOKEN = "8525943988:AAHVoaX2JXmXVZnbdGVg0T4McCEa-NHMA5U"  # MyAntiGravityClawBot
TELEGRAM_CHAT_ID = "-1003831532042"
TELEGRAM_TOPIC = "25"

# Track state
last_alert_time = {}
ALERT_COOLDOWN = 300  # 5 minutes between same alerts


def load_telegram_config():
    """Load Telegram bot token from OpenClaw config"""
    global TELEGRAM_TOKEN
    try:
        import os
        TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not TELEGRAM_TOKEN:
            # Try reading from config
            config_path = os.path.expanduser("~/.openclaw/config.yaml")
            if os.path.exists(config_path):
                with open(config_path) as f:
                    for line in f:
                        if "telegram" in line.lower() and "token" in line.lower():
                            TELEGRAM_TOKEN = line.split(":")[-1].strip().strip('"')
                            break
    except:
        pass


def send_telegram_alert(message):
    """Send alert to Telegram"""
    if not TELEGRAM_TOKEN:
        print(f"[ALERT] {message}")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "message_thread_id": int(TELEGRAM_TOPIC),
            "parse_mode": "HTML",
        }
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def check_alerts(symbol, price):
    """Check if price triggers any alerts"""
    if symbol not in ALERTS:
        return
    
    info = ALERTS[symbol]
    now = time.time()
    
    # Cooldown check
    if symbol in last_alert_time and (now - last_alert_time[symbol]) < ALERT_COOLDOWN:
        return
    
    alerts = []
    
    # Stop loss
    if info["stop"] > 0 and price <= info["stop"]:
        alerts.append(f"🚨 STOP LOSS HIT: ${price:.4f} (stop: ${info['stop']:.4f})")
    
    # Take profit
    if info["tp"] > 0 and price >= info["tp"]:
        alerts.append(f"🎯 TAKE PROFIT HIT: ${price:.4f} (target: ${info['tp']:.4f})")
    
    # Entry zone
    if info["entry_low"] <= price <= info["entry_high"]:
        alerts.append(f"🟢 ENTRY ZONE: ${price:.4f} (range: ${info['entry_low']:.4f} — ${info['entry_high']:.4f})")
    
    # Below entry (aggressive buy)
    if price < info["entry_low"] and info["entry_low"] > 0:
        alerts.append(f"🟢 BELOW ENTRY: ${price:.4f} — aggressive buy zone")
    
    # Big move alert (>5% in short time)
    # We track this via price change detection
    
    if alerts:
        last_alert_time[symbol] = now
        header = f"📊 <b>{info['coin']}</b> ({info['tier']} Tier)\n"
        message = header + "\n".join(alerts)
        send_telegram_alert(message)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {info['coin']}: {', '.join(alerts)}")


def on_message(ws, message):
    """Handle WebSocket message"""
    try:
        data = json.loads(message)
        if "s" in data and "p" in data:
            symbol = data["s"]
            price = float(data["p"])
            check_alerts(symbol, price)
    except:
        pass


def on_error(ws, error):
    print(f"WebSocket error: {error}")


def on_close(ws, close_status, close_msg):
    print("WebSocket closed, reconnecting in 5s...")
    time.sleep(5)
    start_websocket()


def on_open(ws):
    symbols = list(ALERTS.keys())
    # Subscribe to mini ticker stream for all pairs
    streams = "/".join([f"{s.lower()}@miniTicker" for s in symbols])
    ws.send(json.dumps({"method": "SUBSCRIBE", "params": [streams], "id": 1}))
    print(f"✅ Monitoring {len(symbols)} pairs: {', '.join(ALERTS[a]['coin'] for a in symbols)}")


def start_websocket():
    symbols = list(ALERTS.keys())
    streams = "/".join([f"{s.lower()}@miniTicker" for s in symbols])
    url = f"wss://stream.binance.com:9443/stream?streams={streams}"
    
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever()


if __name__ == "__main__":
    load_telegram_config()
    print("=" * 50)
    print("🔔 REAL-TIME PRICE ALERT SYSTEM")
    print("=" * 50)
    print(f"Monitoring {len(ALERTS)} pairs")
    print(f"Alert cooldown: {ALERT_COOLDOWN}s")
    print("=" * 50)
    
    # Send startup message
    send_telegram_alert("🔔 <b>Price Alert System Started</b>\nMonitoring: " + ", ".join(ALERTS[a]['coin'] for a in ALERTS))
    
    start_websocket()
