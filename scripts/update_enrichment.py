"""
update_enrichment.py — Apply AI researched content to reports.

Replaces Business Intro, Supply Chain, and Customer sections.
Usage:
  python scripts/update_enrichment.py AAPL enrichment_AAPL.json
"""

import os
import json
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import find_ticker_files, replace_section, normalize_wikilinks

def update_enrichment(filepath, data):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize incoming data wikilinks if needed (done by the script later but good practice)
    intro = data.get("business_intro", "")
    supply_chain = data.get("supply_chain", "")
    customers = data.get("customers", "")

    if intro:
        content = replace_section(content, "## 業務簡介", intro, "## 供應鏈位置")
    if supply_chain:
        content = replace_section(content, "## 供應鏈位置", supply_chain, "## 主要客戶及供應商")
    if customers:
        content = replace_section(content, "## 主要客戶及供應商", customers, "## 財務概況")

    # Final normalization
    content = normalize_wikilinks(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/update_enrichment.py <ticker> <json_file>")
        return
    ticker = sys.argv[1].upper()
    json_file = sys.argv[2]
    
    files = find_ticker_files([ticker])
    if not files:
        print(f"Ticker {ticker} not found.")
        return
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if update_enrichment(files[ticker], data):
        print(f"Updated enrichment for {ticker}")

if __name__ == "__main__":
    main()
