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
                        "inline": True
                    },
                    {
                        "name": "Volume",
                        "value": get_change_info(latest["volume"], previous["volume"]),
                        "inline": True
                    }
                ],
                "image": {
                    "url": "attachment://chart.png"
                },
                "footer": {
                    "text": f"Last Updated: {data.get('updated_at', 'N/A')}"
                }
            }
        ]
    }

    try:
        files = {}
        if os.path.exists("chart.png"):
            files["file"] = ("chart.png", open("chart.png", "rb"), "image/png")

        response = requests.post(
            WEBHOOK_URL, 
            data={"payload_json": json.dumps(payload)}, 
            files=files, 
            timeout=20
        )
        
        if response.status_code < 300:
            print("[+] Discord notification sent successfully.")
        else:
            print(f"[!] Discord API returned status {response.status_code}: {response.text}")
            sys.exit(1)
            
        # Close file if it was opened
        if "file" in files:
            files["file"][1].close()
            
    except Exception as e:
        print(f"[!] Error sending Discord notification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
