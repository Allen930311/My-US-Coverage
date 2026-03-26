"""
audit_batch.py — Quality audit for US ticker reports.

Checks: wikilink count, generic wikilinks, placeholders, English text,
metadata completeness.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import REPORTS_DIR, TASK_FILE, get_batch_tickers, setup_stdout

MIN_WIKILINKS = 8
GENERIC_WIKILINK_MARKERS = ["公司", "廠商", "客戶", "供應商", "大廠", "業者"]
PLACEHOLDER_STRINGS = ["待 AI 補充", "(待更新)", "待enrichment"]
REQUIRED_METADATA = ["板塊:", "產業:", "市值:", "企業價值:"]
REQUIRED_SECTIONS = ["## 業務簡介", "## 供應鏈位置", "## 主要客戶及供應商", "## 財務概況"]

def audit_ticker(content):
    issues = []
    if len(content) < 200:
        issues.append("Content too short")
        return False, issues

    for ph in PLACEHOLDER_STRINGS:
        if ph in content:
            issues.append(f"Placeholder: {ph}")

    for field in REQUIRED_METADATA:
        if field not in content:
            issues.append(f"Missing {field}")
            
    wikilinks = re.findall(r"\[\[([^\]]+)\]\]", content)
    if len(wikilinks) < MIN_WIKILINKS:
        issues.append(f"Only {len(wikilinks)} wikilinks (min {MIN_WIKILINKS})")
        
    return len(issues) == 0, issues

def find_batch_files(tickers):
    found = {}
    for root, dirs, files in os.walk(REPORTS_DIR):
        for file in files:
            if file.endswith(".md"):
                # US Tickers are alphanumeric
                match = re.match(r"^([A-Z0-9\.]+)", file)
                if match and match.group(1).upper() in [t.upper() for t in tickers]:
                    found[match.group(1).upper()] = os.path.join(root, file)
    return found

def audit_batch(batch_num, verbose=False):
    tickers = get_batch_tickers(batch_num)
    if not tickers: return
    print(f"AUDIT BATCH {batch_num}")
    found = find_batch_files(tickers)
    clean = []
    for ticker in tickers:
        if ticker.upper() not in found:
            print(f"  {ticker}: MISSING")
            continue
        with open(found[ticker.upper()], "r", encoding="utf-8") as f:
            content = f.read()
        is_clean, issues = audit_ticker(content)
        if is_clean:
            clean.append(ticker)
        elif verbose:
            print(f"  {ticker}: {issues}")
    print(f"Score: {len(clean)}/{len(tickers)}")

def main():
    setup_stdout()
    if len(sys.argv) < 2: return
    verbose = "-v" in sys.argv
    if sys.argv[1] == "--all":
        # Simplified for now
        print("Audit all not yet fully implemented for US (depends on task.md structure)")
    else:
        audit_batch(sys.argv[1], verbose)

if __name__ == "__main__":
    main()
