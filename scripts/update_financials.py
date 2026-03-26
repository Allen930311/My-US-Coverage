"""
update_financials.py — Refresh financial tables in US ticker reports.

Fetches latest annual (3yr) and quarterly (4Q) data from yfinance,
then replaces ONLY the ## 財務概況 section.
Units: Million USD. Margins in %.
"""

import os
import re
import sys
import time
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    find_ticker_files, parse_scope_args, setup_stdout,
    fetch_valuation_data, build_valuation_table, update_metadata,
)

METRICS_KEYS = {
    "revenue": ["Total Revenue"],
    "gross_profit": ["Gross Profit"],
    "selling_exp": ["Selling And Marketing Expense"],
    "rd_exp": ["Research And Development"],
    "admin_exp": ["General And Administrative Expense"],
    "operating_income": ["Operating Income"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
    "ocf": ["Operating Cash Flow", "Total Cash From Operating Activities"],
    "icf": ["Investing Cash Flow", "Total Cashflows From Investing Activities"],
    "fcf": ["Financing Cash Flow", "Total Cash From Financing Activities"],
    "capex": ["Capital Expenditure", "Capital Expenditures"],
}

def get_series(df, keys):
    for key in keys:
        if key in df.index:
            return df.loc[key]
    return pd.Series(dtype=float)

def calc_margin(numerator, denominator):
    if denominator.empty or numerator.empty:
        return pd.Series(dtype=float)
    result = (numerator / denominator) * 100
    result = result.replace([float("inf"), float("-inf")], float("nan"))
    return result

def extract_metrics(income_stmt, cashflow):
    if income_stmt.empty and cashflow.empty:
        return pd.DataFrame()
    data = {
        "Revenue": get_series(income_stmt, METRICS_KEYS["revenue"]),
        "Gross Profit": get_series(income_stmt, METRICS_KEYS["gross_profit"]),
        "Gross Margin (%)": calc_margin(get_series(income_stmt, METRICS_KEYS["gross_profit"]), get_series(income_stmt, METRICS_KEYS["revenue"])),
        "Selling & Marketing Exp": get_series(income_stmt, METRICS_KEYS["selling_exp"]),
        "R&D Exp": get_series(income_stmt, METRICS_KEYS["rd_exp"]),
        "Operating Income": get_series(income_stmt, METRICS_KEYS["operating_income"]),
        "Operating Margin (%)": calc_margin(get_series(income_stmt, METRICS_KEYS["operating_income"]), get_series(income_stmt, METRICS_KEYS["revenue"])),
        "Net Income": get_series(income_stmt, METRICS_KEYS["net_income"]),
        "Net Margin (%)": calc_margin(get_series(income_stmt, METRICS_KEYS["net_income"]), get_series(income_stmt, METRICS_KEYS["revenue"])),
        "Op Cash Flow": get_series(cashflow, METRICS_KEYS["ocf"]),
        "CAPEX": get_series(cashflow, METRICS_KEYS["capex"]),
    }
    df = pd.DataFrame(data).T
    df.columns = [col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col) for col in df.columns]
    return df

def fetch_financials(ticker):
    """Fetch financial data for US ticker (no suffix)."""
    try:
        stock = yf.Ticker(ticker)
        income = stock.income_stmt
        if income is None or income.empty:
            return None

        df_annual = extract_metrics(stock.income_stmt, stock.cashflow)
        if not df_annual.empty:
            df_annual = df_annual[sorted(df_annual.columns, reverse=True)]
            non_pct = [r for r in df_annual.index if "%" not in r]
            df_annual.loc[non_pct] = df_annual.loc[non_pct] / 1_000_000
            df_annual = df_annual.iloc[:, :3]

        df_quarterly = extract_metrics(stock.quarterly_income_stmt, stock.quarterly_cashflow)
        if not df_quarterly.empty:
            df_quarterly = df_quarterly[sorted(df_quarterly.columns, reverse=True)]
            non_pct = [r for r in df_quarterly.index if "%" not in r]
            df_quarterly.loc[non_pct] = df_quarterly.loc[non_pct] / 1_000_000
            df_quarterly = df_quarterly.iloc[:, :4]

        info = stock.info
        market_cap = f"{info['marketCap'] / 1_000_000:,.0f}" if info.get("marketCap") else None
        enterprise_value = f"{info['enterpriseValue'] / 1_000_000:,.0f}" if info.get("enterpriseValue") else None

        return {
            "annual": df_annual,
            "quarterly": df_quarterly,
            "valuation": fetch_valuation_data(info),
            "market_cap": market_cap,
            "enterprise_value": enterprise_value,
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def build_financial_section(data):
    section = "## 財務概況 (單位: Million USD, 只有 Margin 為 %)\n"
    v = data.get("valuation", {})
    if v:
        section += build_valuation_table(v) + "\n\n"
    section += "### 年度關鍵財務數據 (近 3 年)\n"
    if data["annual"] is not None and not data["annual"].empty:
        section += data["annual"].to_markdown(floatfmt=".2f").replace(" nan ", " - ") + "\n\n"
    else:
        section += "無可用數據。\n\n"
    section += "### 季度關鍵財務數據 (近 4 季)\n"
    if data["quarterly"] is not None and not data["quarterly"].empty:
        section += data["quarterly"].to_markdown(floatfmt=".2f").replace(" nan ", " - ") + "\n"
    else:
        section += "無可用數據。\n"
    return section

def update_file(filepath, ticker, dry_run=False):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    data = fetch_financials(ticker)
    if data is None:
        return False
    new_fin = build_financial_section(data)
    if re.search(r"## 財務概況", content):
        new_content = re.sub(r"## 財務概況.*", new_fin, content, flags=re.DOTALL)
    else:
        new_content = content.rstrip() + "\n\n" + new_fin
    new_content = update_metadata(new_content, data.get("market_cap"), data.get("enterprise_value"), "USD")
    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
    return True

def main():
    setup_stdout()
    args = list(sys.argv[1:])
    dry_run = "--dry-run" in args
    if dry_run: args.remove("--dry-run")
    tickers, sector, desc = parse_scope_args(args)
    files = find_ticker_files(tickers, sector)
    if not files: return
    for ticker in sorted(files.keys()):
        try:
            if update_file(files[ticker], ticker, dry_run):
                print(f"  {ticker}: UPDATED")
            else:
                print(f"  {ticker}: SKIP")
        except Exception as e:
            print(f"  {ticker}: ERROR ({e})")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
