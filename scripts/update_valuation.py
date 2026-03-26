"""
update_valuation.py — Fast refresh of valuation metrics only.

Updates P/E, P/B, P/S, EV/EBITDA and Current Price.
Usage:
  python scripts/update_valuation.py
  python scripts/update_valuation.py AAPL
"""

import os
import re
import sys
import time
import yfinance as yf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    find_ticker_files, parse_scope_args, setup_stdout,
    fetch_valuation_data, build_valuation_table, update_metadata,
)

def update_valuation(filepath, ticker):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or "currentPrice" not in info:
            return False

        valuation = fetch_valuation_data(info)
        new_table = build_valuation_table(valuation)
        
        # Replace the valuation table section
        if "### 估值指標" in content:
            # Match until the next H3 or more
            content = re.sub(r"### 估值指標.*?(?=\n###|\n##|$)", new_table, content, flags=re.DOTALL)
        else:
            # If not found, insert before annual financials
            content = content.replace("### 年度關鍵財務數據", new_table + "\n\n### 年度關鍵財務數據")

        # Update metadata
        market_cap = f"{info['marketCap'] / 1_000_000:,.0f}" if info.get("marketCap") else None
        ev = f"{info['enterpriseValue'] / 1_000_000:,.0f}" if info.get("enterpriseValue") else None
        content = update_metadata(content, market_cap, ev, "USD")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error {ticker}: {e}")
        return False

def main():
    setup_stdout()
    args = sys.argv[1:]
    tickers, sector, desc = parse_scope_args(args)
    files = find_ticker_files(tickers, sector)
    if not files: return
    for ticker in sorted(files.keys()):
        if update_valuation(files[ticker], ticker):
            print(f"  {ticker}: VALUATION UPDATED")
        time.sleep(0.3)

if __name__ == "__main__":
    main()
