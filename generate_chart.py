import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

DATA_FILE = "data/gold_oi.json"
OUTPUT_FILE = "chart.png"

def generate_chart():
    if not os.path.exists(DATA_FILE):
        print(f"[!] Data file {DATA_FILE} not found.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    records = data.get("records", [])
    if not records:
        print("[!] No records found in data file.")
        return

    # Keep only the last 20 records
    records = records[-20:]

    dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in records]
    volumes = [r["volume"] for r in records]
    oi = [r["open_interest"] for r in records]

    # Set dark theme style
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # X-axis formatting
    ax1.set_xlabel('Date', color='white', fontsize=10)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45)

    # Primary Y-axis: Volume (Bars)
    color_vol = 'skyblue'
    ax1.set_ylabel('Volume', color=color_vol, fontsize=12, fontweight='bold')
    ax1.bar(dates, volumes, color=color_vol, alpha=0.3, label='Volume')
    ax1.tick_params(axis='y', labelcolor=color_vol)
    ax1.grid(True, alpha=0.1)

    # Secondary Y-axis: Open Interest (Line)
    ax2 = ax1.twinx()
    color_oi = 'white'
    ax2.set_ylabel('Open Interest', color=color_oi, fontsize=12, fontweight='bold')
    ax2.plot(dates, oi, color=color_oi, linewidth=3, marker='o', markersize=6, label='Open Interest')
    ax2.tick_params(axis='y', labelcolor=color_oi)

    # Title and Layout
    plt.title('Gold Futures (GC) - 20 Day Volume & Open Interest', fontsize=16, pad=20, fontweight='bold')
    fig.tight_layout()

    # Save the figure
    plt.savefig(OUTPUT_FILE, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"[+] Chart saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_chart()
