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

    dates = [mdates.date2num(datetime.strptime(r["date"], "%Y-%m-%d")) for r in records]
    opens = [r.get("open", 0) for r in records]
    highs = [r.get("high", 0) for r in records]
    lows = [r.get("low", 0) for r in records]
    closes = [r.get("close", 0) for r in records]
    volumes = [r["volume"] for r in records]
    oi = [r["open_interest"] for r in records]
    dxy = [r.get("dxy", 0) for r in records]

    plt.style.use('dark_background')
    fig, (ax_top, ax_bot) = plt.subplots(nrows=2, ncols=1, figsize=(12, 10), 
                                         height_ratios=[3, 1], sharex=True)

    # --- Top Panel: Candlesticks, OI, DXY ---
    
    # Candlesticks
    width = 0.6
    for i in range(len(dates)):
        color = 'lightgreen' if closes[i] >= opens[i] else 'lightred'
        # Wick
        ax_top.vlines(dates[i], lows[i], highs[i], color=color, linewidth=1, alpha=0.5)
        # Body
        ax_top.bar(dates[i], closes[i] - opens[i], width, bottom=opens[i], 
                   color=color, alpha=0.4, edgecolor=color)
        # Red dot on close
        ax_top.scatter(dates[i], closes[i], color='red', s=20, zorder=5)

    ax_top.set_ylabel('Gold Price (USD)', color='white', fontsize=12, fontweight='bold')
    ax_top.tick_params(axis='y', labelcolor='white')
    ax_top.grid(True, alpha=0.1)

    # Open Interest (Primary Secondary Y-axis)
    ax_oi = ax_top.twinx()
    ax_oi.plot(dates, oi, color='white', linewidth=3, label='Open Interest')
    ax_oi.set_ylabel('Open Interest', color='white', fontsize=12, fontweight='bold')
    ax_oi.tick_params(axis='y', labelcolor='white')

    # DXY (Secondary Secondary Y-axis)
    ax_dxy = ax_top.twinx()
    # Offset dxy axis to not overlap with OI
    ax_dxy.spines['right'].set_position(('outward', 60))
    ax_dxy.plot(dates, dxy, color='gray', alpha=0.3, linestyle='--', linewidth=1.5, label='DXY Index')
    ax_dxy.set_ylabel('DXY Index', color='gray', fontsize=10)
    ax_dxy.tick_params(axis='y', labelcolor='gray')

    ax_top.set_title('Gold Futures (GC) - 20 Day Analysis', fontsize=16, pad=20, fontweight='bold')

    # --- Bottom Panel: Volume ---
    color_vol = 'skyblue'
    ax_bot.bar(dates, volumes, color=color_vol, alpha=0.6, label='Volume')
    ax_bot.set_ylabel('Volume', color=color_vol, fontsize=12, fontweight='bold')
    ax_bot.tick_params(axis='y', labelcolor=color_vol)
    ax_bot.grid(True, alpha=0.1)

    # X-axis formatting
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax_bot.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45)

    fig.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"[+] Chart saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_chart()
