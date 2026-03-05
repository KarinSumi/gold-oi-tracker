import os
import sys
import json
import requests
from datetime import datetime

DATA_FILE = "data/gold_oi.json"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def format_number(n):
    return "{:,}".format(n)

def get_change_info(current, previous):
    diff = current - previous
    percent = (diff / previous) * 100 if previous != 0 else 0
    sign = "+" if diff >= 0 else ""
    return f"{format_number(current)} ({sign}{format_number(diff)} / {sign}{percent:.2f}%)"

def generate_ascii_chart(records):
    if not records:
        return "No data available."
    
    # Last 7 records
    last_7 = records[-7:]
    max_oi = max(r["open_interest"] for r in last_7)
    chart_lines = []
    
    for r in last_7:
        bar_len = int((r["open_interest"] / max_oi) * 15) if max_oi > 0 else 0
        bar = "█" * bar_len
        date_short = r["date"][5:] # MM-DD
        chart_lines.append(f"`{date_short}` {bar}")
    
    return "\n".join(chart_lines)

def main():
    if not WEBHOOK_URL:
        print("[!] DISCORD_WEBHOOK_URL environment variable is missing.")
        sys.exit(1)

    if not os.path.exists(DATA_FILE):
        print(f"[!] Data file {DATA_FILE} not found.")
        sys.exit(0)

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[!] Error reading data: {e}")
        sys.exit(1)

    records = data.get("records", [])
    if len(records) < 2:
        print("[!] Not enough data records to send notification.")
        sys.exit(0)

    # Sort records by date to be sure
    records.sort(key=lambda x: x["date"])
    
    latest = records[-1]
    previous = records[-2]

    oi_up = latest["open_interest"] >= previous["open_interest"]
    embed_color = 3066993 if oi_up else 15158332 # Green or Red (decimal)

    payload = {
        "embeds": [
            {
                "title": "⬡ Gold Futures (GC) — Daily OI Report",
                "color": embed_color,
                "fields": [
                    {
                        "name": "Open Interest",
                        "value": get_change_info(latest["open_interest"], previous["open_interest"]),
                        "inline": False
                    },
                    {
                        "name": "Volume",
                        "value": get_change_info(latest["volume"], previous["volume"]),
                        "inline": False
                    },
                    {
                        "name": "OI Trend (Last 7 Trading Days)",
                        "value": generate_ascii_chart(records),
                        "inline": False
                    }
                ],
                "footer": {
                    "text": f"Last Updated: {data.get('updated_at', 'N/A')}"
                }
            }
        ]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code < 300:
            print("[+] Discord notification sent successfully.")
        else:
            print(f"[!] Discord API returned status {response.status_code}: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"[!] Error sending Discord notification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
