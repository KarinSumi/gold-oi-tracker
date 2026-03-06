import os
import json
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

def main():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    data = load_data()
    
    print("[*] Fetching data from Yahoo Finance (GC=F)...")
    try:
        ticker = yf.Ticker("GC=F")
        info = ticker.info
        
        # Yahoo Finance often has volume and openInterest in info
        volume = info.get("volume") or info.get("regularMarketVolume")
        oi = info.get("openInterest")
        
        if volume is not None and oi is not None:
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            # Update or append today's record
            record_found = False
            for r in data["records"]:
                if r["date"] == today_str:
                    r["volume"] = volume
                    r["open_interest"] = oi
                    record_found = True
                    break
            
            if not record_found:
                data["records"].append({
                    "date": today_str,
                    "volume": volume,
                    "open_interest": oi
                })
            
            print(f"[+] Successfully fetched data for {today_str}: Vol={volume}, OI={oi}")
            save_data(data)
        else:
            print("[!] Could not find Volume or Open Interest in Yahoo Finance data.")
            # Still save to ensure base structure/updated_at if needed, 
            # but usually we want to know it failed.
            if not data["records"]:
                save_data(data)

    except Exception as e:
        print(f"[!] Error fetching from Yahoo Finance: {e}")
        if not data["records"]:
             save_data(data)

if __name__ == "__main__":
    main()
