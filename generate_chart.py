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
    volumes = [r.get("volume", 0) for r in records]
    oi = [r.get("open_interest", 0) for r in records]
    dxy = [r.get("dxy", 0) for r in records]
    managed_money = [r.get("net_managed_money", 0) for r in records]
    commercials = [r.get("net_commercials", 0) for r in records]

    plt.style.use('dark_background')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14), 
                                         gridspec_kw={'height_ratios': [3, 1, 1.5]}, 
                                         sharex=True)

    # --- Top Panel: ax1 - Price, OI, DXY ---
    width = 0.6
    for i in range(len(dates)):
        color = 'lightgreen' if closes[i] >= opens[i] else 'lightred'
        # Wick
        ax1.vlines(dates[i], lows[i], highs[i], color=color, linewidth=1, alpha=0.5)
        # Body (open/close bar)
        ax1.bar(dates[i], closes[i] - opens[i], width, bottom=opens[i], 
                color=color, alpha=0.4, edgecolor=color)
        # Red dot on close
        ax1.scatter(dates[i], closes[i], color='red', s=25, zorder=5)

    ax1.set_ylabel('Gold Price (USD)', color='white', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='white')
    ax1.grid(True, alpha=0.1)

    # OI on secondary Y-axis
    ax1_oi = ax1.twinx()
    ax1_oi.plot(dates, oi, color='white', linewidth=3, label='Open Interest')
    ax1_oi.set_ylabel('Open Interest', color='white', fontsize=12)
    ax1_oi.tick_params(axis='y', labelcolor='white')

    # DXY on tertiary Y-axis
    ax1_dxy = ax1.twinx()
    ax1_dxy.spines['right'].set_position(('axes', 1.1))
    ax1_dxy.plot(dates, dxy, color='gray', alpha=0.4, linestyle='--', linewidth=1.5, label='DXY Index')
    ax1_dxy.set_ylabel('DXY Index', color='gray', fontsize=10)
    ax1_dxy.tick_params(axis='y', labelcolor='gray')

    ax1.set_title('Gold Futures (GC) - Multi-Factor Analysis', fontsize=16, pad=20, fontweight='bold')

    # --- Middle Panel: ax2 - Volume ---
    ax2.bar(dates, volumes, color='skyblue', alpha=0.6, label='Volume')
    ax2.set_ylabel('Volume', color='skyblue', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='skyblue')
    ax2.grid(True, alpha=0.1)

    # --- Bottom Panel: ax3 - COT ---
    ax3.plot(dates, managed_money, color='lime', linewidth=2, label='Net Managed Money')
    ax3.plot(dates, commercials, color='red', linewidth=2, label='Net Commercials')
    ax3.axhline(0, color='white', linestyle='-', alpha=0.2, linewidth=1)
    ax3.set_ylabel('COT Net Positions', color='white', fontsize=12)
    ax3.legend(loc='upper left', fontsize=10)
    ax3.grid(True, alpha=0.1)

    # X-axis formatting
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax3.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45)

    fig.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"[+] Chart saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_chart()
