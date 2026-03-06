import os
import json
import requests
import yfinance as yf
from datetime import datetime

DATA_FILE = "data/gold_oi.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"updated_at": "", "product": "Gold Futures (GC)", "records": []}

def save_data(data):
    data["updated_at"] = datetime.now().isoformat()
    # Sort records by date and keep only the latest 20
    data["records"].sort(key=lambda x: x["date"], reverse=True)
    
    # Remove duplicates by date
    unique_records = []
    seen_dates = set()
    for r in data["records"]:
        if r["date"] not in seen_dates:
            unique_records.append(r)
            seen_dates.add(r["date"])
    
    data["records"] = unique_records[:20]
    data["records"].sort(key=lambda x: x["date"])  # Store in ascending order
    
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def fetch_cot_data():
    print("[*] Fetching CFTC COT data...")
    url = "https://publicreporting.cftc.gov/resource/72hh-3qpy.json?cftc_contract_market_code=088691&$limit=1&$order=report_date_as_yyyy_mm_dd%20DESC"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            cot_json = response.json()
            if cot_json:
                latest = cot_json[0]
                net_managed_money = int(latest.get("m_money_positions_long_all", 0)) - int(latest.get("m_money_positions_short_all", 0))
                net_commercials = int(latest.get("prod_merc_positions_long_all", 0)) - int(latest.get("prod_merc_positions_short_all", 0))
                return net_managed_money, net_commercials
    except Exception as e:
        print(f"    [!] Error fetching COT data: {e}")
    return 0, 0

def main():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    data = load_data()
    
    print("[*] Fetching data from Yahoo Finance...")
    try:
        # Fetch Gold Futures
        gold_ticker = yf.Ticker("GC=F")
        gold_hist = gold_ticker.history(period="5d")
        
        if not gold_hist.empty:
            latest_bar = gold_hist.iloc[-1]
            g_open = float(latest_bar["Open"])
            g_high = float(latest_bar["High"])
            g_low = float(latest_bar["Low"])
            g_close = float(latest_bar["Close"])
            volume = int(latest_bar["Volume"])
        else:
            print("[!] No Gold history found.")
            return

        # Fetch additional info for OI
        gold_info = gold_ticker.info
        oi = gold_info.get("openInterest") or 0
        
        # Fetch DXY
        dxy_ticker = yf.Ticker("DX-Y.NYB")
        dxy_close = dxy_ticker.info.get("regularMarketPreviousClose") or dxy_ticker.info.get("previousClose") or 0
        
        # Fetch COT
        net_managed_money, net_commercials = fetch_cot_data()

        today_str = datetime.now().strftime("%Y-%m-%d")
        
        new_record = {
            "date": today_str,
            "volume": volume,
            "open_interest": oi,
            "open": round(g_open, 2),
            "high": round(g_high, 2),
            "low": round(g_low, 2),
            "close": round(g_close, 2),
            "dxy": round(dxy_close, 3),
            "net_managed_money": net_managed_money,
            "net_commercials": net_commercials
        }
        
        # Update or append today's record
        record_found = False
        for i, r in enumerate(data["records"]):
            if r["date"] == today_str:
                # Merge with existing to keep older fields if any
                data["records"][i].update(new_record)
                record_found = True
                break
        
        if not record_found:
            data["records"].append(new_record)
        
        print(f"[+] Successfully fetched data for {today_str}")
        save_data(data)

    except Exception as e:
        print(f"[!] Error in main fetch: {e}")

if __name__ == "__main__":
    main()
