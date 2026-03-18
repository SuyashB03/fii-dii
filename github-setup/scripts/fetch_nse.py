#!/usr/bin/env python3
"""
Fetches FII/DII cash market data from NSE India and saves to data/latest.json
Runs via GitHub Actions every weekday at 4:30 PM IST.
"""

import requests
import json
import os
from datetime import datetime

# ── NSE API config ────────────────────────────────────────────────────────────
NSE_URL   = "https://www.nseindia.com/api/fiidiiTradeReact"
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer":         "https://www.nseindia.com/",
    "Connection":      "keep-alive",
}
OUTPUT_PATH = "data/latest.json"

def fetch_nse():
    session = requests.Session()

    # Step 1: Get NSE homepage to acquire cookies (required for API access)
    print("Getting NSE session cookies...")
    session.get("https://www.nseindia.com", headers=HEADERS, timeout=15)

    # Step 2: Fetch actual FII/DII data
    print("Fetching FII/DII data...")
    resp = session.get(NSE_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    raw = resp.json()
    if not isinstance(raw, list) or len(raw) == 0:
        raise ValueError(f"Unexpected response format: {raw}")

    # Step 3: Parse rows
    result = {
        "date":     "",
        "fii_buy":  0.0,
        "fii_sell": 0.0,
        "fii_net":  0.0,
        "dii_buy":  0.0,
        "dii_sell": 0.0,
        "dii_net":  0.0,
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    for row in raw:
        cat = (row.get("category") or "").upper()
        if "FII" in cat or "FPI" in cat:
            result["fii_buy"]  = float(row.get("buyValue")  or 0)
            result["fii_sell"] = float(row.get("sellValue") or 0)
            result["fii_net"]  = float(row.get("netValue")  or 0)
            result["date"]     = row.get("date") or ""
        elif "DII" in cat:
            result["dii_buy"]  = float(row.get("buyValue")  or 0)
            result["dii_sell"] = float(row.get("sellValue") or 0)
            result["dii_net"]  = float(row.get("netValue")  or 0)

    if not result["date"]:
        raise ValueError("Could not find FII/DII row in response")

    print(f"Date   : {result['date']}")
    print(f"FII Net: {result['fii_net']}")
    print(f"DII Net: {result['dii_net']}")

    # Step 4: Save to file
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    fetch_nse()
