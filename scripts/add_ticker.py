"""
add_ticker.py — Generate a new US ticker report with financials.
Usage:
  python scripts/add_ticker.py AAPL Apple
"""
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import find_ticker_files, REPORTS_DIR
from update_financials import fetch_financials, build_financial_section

def generate_report(ticker, name, sector=None, industry=None):
    fin_data = fetch_financials(ticker)
    if fin_data:
        sector = sector or fin_data.get("sector", "Unknown")
        industry = industry or fin_data.get("industry", "Unknown")
        market_cap = fin_data.get("market_cap", "N/A")
        enterprise_value = fin_data.get("enterprise_value", "N/A")
        fin_section = build_financial_section(fin_data)
    else:
        sector = sector or "Unknown"
        industry = industry or "Unknown"
        market_cap = "N/A"
        enterprise_value = "N/A"
        fin_section = "## 財務概況 (單位: Million USD)\n### 年度關鍵財務數據\n無可用數據。\n"

    content = f"""# {ticker} - [[{name}]]

## 業務簡介
**板塊:** {sector}
**產業:** {industry}
**市值:** {market_cap} Million USD
**企業價值:** {enterprise_value} Million USD

*(待enrichment — 請使用 /update-enrichment 補充業務描述)*

## 供應鏈位置
*(待enrichment)*

## 主要客戶及供應商
*(待enrichment)*

{fin_section}"""
    return content, sector

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python scripts/add_ticker.py <ticker> <name>")
        return
    ticker = args[0].upper()
    name = args[1]
    
    sector = None
    if "--sector" in args:
        idx = args.index("--sector")
        sector = " ".join(args[idx + 1 :])

    existing = find_ticker_files([ticker])
    if existing:
        print(f"Ticker {ticker} already exists.")
        return

    print(f"Generating report for {ticker} ({name})...")
    content, detected_sector = generate_report(ticker, name, sector)
    
    folder_name = re.sub(r'[<>:"/\\|?*]', "", detected_sector).strip()
    output_dir = os.path.join(REPORTS_DIR, folder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, f"{ticker}_{name}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {filepath}")

if __name__ == "__main__":
    main()
