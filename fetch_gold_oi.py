import os
import json
import time
from curl_cffi import requests
from datetime import datetime, timedelta

DATA_FILE = "data/gold_oi.json"
PRODUCT_ID = 437  # Gold Futures (GC)
BASE_URL = "https://www.cmegroup.com/CmeWS/mvc/Volume/VolumeOpenInterest"

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
    data["records"] = data["records"][:20]
    data["records"].sort(key=lambda x: x["date"])  # Store in ascending order
    
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def fetch_date_data(date_str):
    url = f"{BASE_URL}?productId={PRODUCT_ID}&tradeDate={date_str}"
    print(f"[*] Fetching data for {date_str}...")
    try:
        # Using curl_cffi to impersonate Chrome 110 TLS fingerprint
        response = requests.get(url, impersonate="chrome110", timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            # CME returns null volume/OI if data isn't ready yet
            vol = res_data.get("totalVolume")
            oi = res_data.get("totalOpenInterest")
            
            if vol is not None and oi is not None:
                # Remove commas if present in string response
                vol = int(str(vol).replace(",", ""))
                oi = int(str(oi).replace(",", ""))
                return {"volume": vol, "open_interest": oi}
            else:
                print(f"    [!] No data available for {date_str} (yet)")
        elif response.status_code in [401, 403]:
            print(f"    [!] BLOCKED: API returned {response.status_code}. Cloudflare protection triggered.")
        else:
            print(f"    [!] API returned status code {response.status_code}")
    except Exception as e:
        print(f"    [!] Error fetching {date_str}: {e}")
    return None

def main():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    data = load_data()
    existing_dates = {r["date"] for r in data["records"]}
    
    today = datetime.now()
    fetched_count = 0
    
    # Check last 5 calendar days to ensure we get the latest data
    for i in range(5):
        if len(data["records"]) >= 20:
            break
            
        target_date = today - timedelta(days=i)
        
        # Skip weekends
        if target_date.weekday() >= 5:
            continue
            
        date_iso = target_date.strftime("%Y-%m-%d")
        date_cme = target_date.strftime("%Y%m%d")
        
        if date_iso in existing_dates:
            continue
            
        result = fetch_date_data(date_cme)
        if result:
            data["records"].append({
                "date": date_iso,
                "volume": result["volume"],
                "open_interest": result["open_interest"]
            })
            fetched_count += 1
            # Rate limiting sleep
            time.sleep(0.8)
            
    save_data(data)
    if fetched_count > 0:
        print(f"[+] Successfully fetched {fetched_count} new records.")
    else:
        print("[*] No new data found (base structure ensured).")

if __name__ == "__main__":
    main()
