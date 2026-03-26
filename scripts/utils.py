"""
utils.py — Shared utilities for My-US-Coverage scripts.

Provides: file discovery, batch parsing, scope parsing, wikilink normalization,
category classification, valuation table rendering, metadata updates.
"""

import os
import re
import sys
import glob
from datetime import date, datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "Pilot_Reports")
TASK_FILE = os.path.join(PROJECT_ROOT, "task.md")


# =============================================================================
# File Discovery
# =============================================================================

def find_ticker_files(tickers=None, sector=None):
    """Find report files matching given tickers or sector.
    Returns dict: {ticker: filepath}
    """
    files = {}
    for fp in glob.glob(os.path.join(REPORTS_DIR, "**", "*.md"), recursive=True):
        fn = os.path.basename(fp)
        # US tickers are alphanumeric (e.g., AAPL_Apple.md)
        m = re.match(r"^([A-Z0-9\.]+)_", fn)
        if not m:
            continue
        t = m.group(1)

        if sector:
            folder = os.path.basename(os.path.dirname(fp))
            if folder.lower() != sector.lower():
                continue

        if tickers is None or t.upper() in [tk.upper() for tk in tickers]:
            files[t] = fp

    return files


def get_ticker_from_filename(filepath):
    """Extract ticker symbol and company name from a report filename."""
    fn = os.path.basename(filepath)
    m = re.match(r"^([A-Z0-9\.]+)_(.+)\.md$", fn)
    if m:
        return m.group(1), m.group(2)
    return None, None


# =============================================================================
# Batch & Scope Parsing
# =============================================================================

def get_batch_tickers(batch_num):
    """Get ticker list for a batch from task.md."""
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading task.md: {e}")
        return []

    pattern = re.compile(
        r"Batch\s+" + str(batch_num) + r"\*\*.*?:[:\s]*(.*)$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(content)
    if match:
        raw = match.group(1).strip().rstrip(".")
        # Split by comma and extract ticker (alphanumeric)
        return [
            re.search(r"([A-Z0-9\.]+)", t).group(1)
            for t in raw.split(",")
            if re.search(r"[A-Z0-9\.]+", t)
        ]
    print(f"Error: Batch {batch_num} not found in task.md")
    return []


def parse_scope_args(args):
    """Parse CLI arguments into scope: tickers list, sector, or None (all).
    Returns (tickers_list_or_None, sector_or_None, description_string)
    """
    if not args:
        return None, None, "ALL tickers"
    elif args[0] == "--batch":
        if len(args) < 2:
            print("Error: --batch requires a batch number")
            sys.exit(1)
        batch_num = args[1]
        tickers = get_batch_tickers(batch_num)
        return tickers, None, f"{len(tickers)} tickers in Batch {batch_num}"
    elif args[0] == "--sector":
        if len(args) < 2:
            print("Error: --sector requires a sector name")
            sys.exit(1)
        sector = " ".join(args[1:])
        return None, sector, f"all tickers in sector: {sector}"
    else:
        # Match alphanumeric tickers (upper)
        tickers = [t.strip().upper() for t in args if re.match(r"^[A-Z0-9\.]+$", t.strip().upper())]
        return tickers, None, f"{len(tickers)} tickers: {', '.join(tickers)}"


def setup_stdout():
    """Configure stdout for UTF-8 on Windows."""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# Wikilink Normalization
# =============================================================================

# Canonical name mapping: alias -> canonical
# For US project, canonical name is the ENGLISH name (since most are US/International).
WIKILINK_ALIASES = {
    # Chinese aliases -> English canonical
    "台積電": "TSMC", "聯發科": "MediaTek", "鴻海": "Foxconn",
    "艾司摩爾": "ASML", "應用材料": "Applied Materials", "AMAT": "Applied Materials",
    "東京威力": "Tokyo Electron", "TEL": "Tokyo Electron",
    "科林研發": "Lam Research", "科磊": "KLA", "愛德萬": "Advantest",
    "英特爾": "Intel", "高通": "Qualcomm", "博通": "Broadcom",
    "輝達": "NVIDIA", "美光": "Micron", "海力士": "SK Hynix",
    "英飛凌": "Infineon", "恩智浦": "NXP", "瑞薩": "Renesas",
    "德州儀器": "Texas Instruments", "意法半導體": "STMicroelectronics",
    "安森美": "ON Semiconductor",
    "蘋果": "Apple", "三星": "Samsung", "索尼": "Sony",
    "谷歌": "Alphabet", "Google": "Alphabet", "微軟": "Microsoft", "特斯拉": "Tesla",
    "亞馬遜": "Amazon", "亞馬遜網路服務": "AWS", "臉書": "Meta", "Facebook": "Meta",
    "戴爾": "Dell", "惠普": "HP", "聯想": "Lenovo", "思科": "Cisco",
    "新思": "Synopsys", "益華": "Cadence", "安謀": "Arm", "ARM": "Arm",
    "博世": "Bosch", "電裝": "Denso",
    "信越": "Shin-Etsu", "信越化學": "Shin-Etsu",
    "味之素": "Ajinomoto", "西門子": "Siemens", "漢威": "Honeywell",
    "愛迪達": "Adidas", "耐吉": "Nike", "耐克": "Nike",
    # Specific US Tickers aliases
    "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "GOOG": "Alphabet", "GOOGL": "Alphabet",
    "TSLA": "Tesla", "AMZN": "Amazon", "META": "Meta", "BRK.B": "Berkshire Hathaway",
    # Tech terms: standardize
    "SiC": "碳化矽", "GaN": "氮化鎵", "InP": "磷化銦", "GaAs": "砷化鎵",
    "共封裝光學": "CPO", "Co-Packaged Optics": "CPO",
    "IoT": "物聯網", "EV": "電動車", "印刷電路板": "PCB",
}


def normalize_wikilinks(content):
    """Normalize all wikilinks in content to canonical names.
    Also collapses duplicate parentheticals like [[X]] ([[X]]).
    Only operates on text before 財務概況 to protect financial tables.
    """
    parts = content.split("## 財務概況")
    if len(parts) < 2:
        return content

    text = parts[0]

    # Step 1: Replace alias wikilinks with canonical names
    for alias, canonical in WIKILINK_ALIASES.items():
        text = text.replace("[[" + alias + "]]", "[[" + canonical + "]]")

    # Step 2: Collapse [[X]] ([[X]]) duplicate parentheticals
    text = re.sub(
        r"\[\[([^\]]+)\]\]\s*[\(（]\[\[([^\]]+)\]\][\)）]",
        lambda m: f"[[{m.group(1)}]]" if m.group(1) == m.group(2) else m.group(0),
        text,
    )

    return text + "## 財務概況" + parts[1]


# =============================================================================
# Category Classification
# =============================================================================

TECH_TERMS = {
    "AI", "PCB", "5G", "HBM", "CoWoS", "InFO", "EUV", "CPO", "FOPLP",
    "VCSEL", "EML", "MLCC", "MOSFET", "IGBT", "DRAM", "NAND", "SSD",
    "DDR5", "DDR4", "PCIe", "USB", "WiFi", "Bluetooth", "OLED", "AMOLED",
    "Mini LED", "Micro LED", "MCU", "SoC", "ASIC", "FPGA", "RF", "IC",
    "LED", "LCD", "TFT", "CMP", "CVD", "PVD", "ALD", "AOI", "SMT",
    "BGA", "QFN", "SOP", "ABF", "SerDes", "PMIC", "LDO", "NOR Flash",
    "NAND Flash", "矽光子", "光收發模組", "Quantum Computing", "Generative AI",
}

MATERIAL_TERMS = {
    "碳化矽", "氮化鎵", "磷化銦", "砷化鎵", "矽晶圓", "銅箔", "玻纖布",
    "光阻液", "研磨液", "超純水", "氦氣", "氖氣", "聚醯亞胺",
    "探針卡", "銀漿", "銅漿", "氧化鋁", "Rare Earth", "Lithium", "Cobalt",
}

APPLICATION_TERMS = {
    "AI 伺服器", "電動車", "物聯網", "資料中心", "低軌衛星", "5G",
    "智慧家庭", "車用電子", "消費電子", "綠能", "智慧城市", "Drones", "Edge AI",
}

CATEGORY_COLORS = {
    "us_company": "#3498db",
    "international_company": "#e67e22",
    "technology": "#2ecc71",
    "material": "#f39c12",
    "application": "#9b59b6",
}

CATEGORY_LABELS = {
    "us_company": "美股公司",
    "international_company": "外部公司",
    "technology": "技術/標準",
    "material": "材料/基板",
    "application": "終端應用",
}


def is_cjk(s):
    """Check if a string is primarily CJK characters."""
    return sum(1 for c in s if "\u4e00" <= c <= "\u9fff") > len(s) * 0.3


def classify_wikilink(name):
    """Classify a wikilink into a category."""
    if name in TECH_TERMS:
        return "technology"
    if name in MATERIAL_TERMS:
        return "material"
    if name in APPLICATION_TERMS:
        return "application"
    
    # In US project, we distinguish by ticker existence or context
    # For now, let's assume non-CJK names are international/US companies
    if is_cjk(name):
        return "international_company"
    return "us_company"


# =============================================================================
# Valuation Table Rendering
# =============================================================================

def fetch_valuation_data(info):
    """Extract valuation multiples from yfinance info dict."""
    valuation = {}
    for key, label in [
        ("trailingPE", "P/E (TTM)"),
        ("forwardPE", "Forward P/E"),
        ("priceToSalesTrailing12Months", "P/S (TTM)"),
        ("priceToBook", "P/B"),
        ("enterpriseToEbitda", "EV/EBITDA"),
    ]:
        val = info.get(key)
        valuation[label] = f"{val:.2f}" if val else "N/A"

    # Price
    cur_price = info.get("currentPrice")
    valuation["_price"] = f"{cur_price:,.2f}" if cur_price else None

    # Period info
    mrq = info.get("mostRecentQuarter")
    nfy = info.get("nextFiscalYearEnd")
    valuation["_ttm_end"] = (
        datetime.fromtimestamp(mrq).strftime("%Y-%m-%d") if mrq else None
    )
    valuation["_fwd_end"] = (
        datetime.fromtimestamp(nfy).strftime("%Y-%m-%d") if nfy else None
    )

    return valuation


def build_valuation_table(v):
    """Build the 估值指標 markdown section from valuation dict."""
    headers = ["P/E (TTM)", "Forward P/E", "P/S (TTM)", "P/B", "EV/EBITDA"]
    values = [v.get(h, "N/A") for h in headers]
    widths = [max(len(h), len(val)) for h, val in zip(headers, values)]
    header_row = "| " + " | ".join(h.rjust(w) for h, w in zip(headers, widths)) + " |"
    sep_row = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    val_row = "| " + " | ".join(val.rjust(w) for val, w in zip(values, widths)) + " |"

    today = date.today().strftime("%Y-%m-%d")
    period_parts = []
    if v.get("_price"):
        period_parts.append(f"Price ${v['_price']} (USD) as of {today}")
    if v.get("_ttm_end"):
        period_parts.append(f"TTM end {v['_ttm_end']}")
    if v.get("_fwd_end"):
        period_parts.append(f"Forward to {v['_fwd_end']}")
    period_note = " | ".join(period_parts) if period_parts else ""

    title = f"### 估值指標 ({period_note})\n" if period_note else "### 估值指標\n"
    return title + header_row + "\n" + sep_row + "\n" + val_row


def update_metadata(content, market_cap, enterprise_value, currency="USD"):
    """Update 市值 and 企業價值 metadata in file content."""
    unit = f"Million {currency}"
    if market_cap:
        content = re.sub(
            r"(\*\*市值:\*\*) .+?Million USD",
            rf"\1 {market_cap} {unit}",
            content,
        )
        # Fallback for initial template which might have TWD if copied from TW
        content = re.sub(
            r"(\*\*市值:\*\*) .+?百萬台幣",
            rf"\1 {market_cap} {unit}",
            content,
        )
    if enterprise_value:
        content = re.sub(
            r"(\*\*企業價值:\*\*) .+?Million USD",
            rf"\1 {enterprise_value} {unit}",
            content,
        )
        content = re.sub(
            r"(\*\*企業價值:\*\*) .+?百萬台幣",
            rf"\1 {enterprise_value} {unit}",
            content,
        )
    return content


# =============================================================================
# Section Replacement
# =============================================================================

def replace_section(content, section_header, new_body, next_section_header=None):
    """Replace content between section_header and next_section_header."""
    if next_section_header:
        pattern = rf"({re.escape(section_header)}\n)(.*?)(?=\n{re.escape(next_section_header)})"
        return re.sub(pattern, rf"\g<1>{new_body}\n", content, flags=re.DOTALL)
    else:
        pattern = rf"{re.escape(section_header)}.*"
        return re.sub(pattern, f"{section_header}\n{new_body}\n", content, flags=re.DOTALL)
