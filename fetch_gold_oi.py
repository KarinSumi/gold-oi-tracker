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
    
    print("[*] Fetching data from Yahoo Finance...")
    try:
        # Fetch Gold Futures
        gold_ticker = yf.Ticker("GC=F")
        gold_info = gold_ticker.info
        
        # Fetch DXY
        dxy_ticker = yf.Ticker("DX-Y.NYB")
        dxy_info = dxy_ticker.info
        
        volume = gold_info.get("volume") or gold_info.get("regularMarketVolume")
        oi = gold_info.get("openInterest")
        
        # OHLC for Gold
        g_open = gold_info.get("open") or gold_info.get("regularMarketOpen")
        g_high = gold_info.get("dayHigh") or gold_info.get("regularMarketDayHigh")
        g_low = gold_info.get("dayLow") or gold_info.get("regularMarketDayLow")
        g_close = gold_info.get("previousClose") or gold_info.get("regularMarketPreviousClose")
        
        # DXY Close
        dxy_close = dxy_info.get("previousClose") or dxy_info.get("regularMarketPreviousClose") or 0
        
        if volume is not None and oi is not None:
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            new_record = {
                "date": today_str,
                "volume": volume,
                "open_interest": oi,
                "open": g_open or 0,
                "high": g_high or 0,
                "low": g_low or 0,
                "close": g_close or 0,
                "dxy": dxy_close
            }
            
            # Update or append today's record
            record_found = False
            for i, r in enumerate(data["records"]):
                if r["date"] == today_str:
                    data["records"][i] = new_record
                    record_found = True
                    break
            
            if not record_found:
                data["records"].append(new_record)
            
            print(f"[+] Successfully fetched data for {today_str}")
            save_data(data)
        else:
            print("[!] Essential data (Volume/OI) missing from Yahoo Finance.")

    except Exception as e:
        print(f"[!] Error fetching from Yahoo Finance: {e}")

if __name__ == "__main__":
    main()
