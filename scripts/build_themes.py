"""
build_themes.py — Generate thematic investment screens for US market.
Usage:
  python scripts/build_themes.py
"""

import os
import re
import sys
from collections import defaultdict

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "Pilot_Reports")
THEMES_DIR = os.path.join(os.path.dirname(__file__), "..", "themes")

THEME_DEFINITIONS = {
    "NVIDIA": {
        "name": "NVIDIA & AI Accelerators",
        "desc": "GPUs and custom ASICs for AI training and inference. The core of the AI boom.",
        "related": ["AI Infrastructure", "Semiconductors", "Cloud Infrastructure"],
    },
    "Apple": {
        "name": "Apple Ecosystem",
        "desc": "iPhone, Services, and the broader hardware supply chain.",
        "related": ["Consumer Electronics", "Semiconductors"],
    },
    "Microsoft": {
        "name": "Microsoft & SaaS",
        "desc": "Azure Cloud and Enterprise Software ecosystem.",
        "related": ["Cloud Infrastructure", "Software"],
    },
    "Tesla": {
        "name": "Tesla & EV Value Chain",
        "desc": "Electric vehicles, battery tech, and autonomous driving.",
        "related": ["Clean Energy", "Semiconductors"],
    },
    "Amazon": {
        "name": "Amazon & AWS",
        "desc": "E-commerce and the world's largest public cloud provider.",
        "related": ["Cloud Infrastructure", "Consumer Retail"],
    },
    "Alphabet": {
        "name": "Alphabet (Google) & Ads",
        "desc": "Search, YouTube, and Google Cloud Platform.",
        "related": ["Cloud Infrastructure", "Digital Advertising"],
    },
    "Meta": {
        "name": "Meta & Social Media",
        "desc": "Facebook, Instagram, and the Metaverse (AI hardware focus).",
        "related": ["Digital Advertising", "AI Infrastructure"],
    },
    "Semiconductors": {
        "name": "Semiconductor Capital Equipment",
        "desc": "ASML, AMAT, and companies providing the machines for chip making.",
        "related": ["NVIDIA", "EUV", "TSMC"],
    },
    "Cloud Infrastructure": {
        "name": "Hyperscale Data Centers",
        "desc": "The infrastructure supporting the digital world (AWS, Azure, GCP).",
        "related": ["AI Infrastructure", "NVIDIA"],
    },
}

def scan_wikilinks():
    wl_map = defaultdict(list)
    for root, dirs, files in os.walk(REPORTS_DIR):
        for f in files:
            if not f.endswith(".md"): continue
            m = re.match(r"^([A-Z0-9\.]+)_(.+)\.md$", f)
            if not m: continue
            ticker, company = m.group(1), m.group(2)
            filepath = os.path.join(root, f)
            with open(filepath, "r", encoding="utf-8") as fh:
                content = fh.read()
            for wl in set(re.findall(r"\[\[([^\]]+)\]\]", content)):
                wl_map[wl].append({"ticker": ticker, "company": company, "sector": os.path.basename(root)})
    return wl_map

def build_theme_page(tag, defn, wl_map):
    entries = wl_map.get(tag, [])
    if not entries: return None
    lines = [f"# {defn['name']}", "", f"> {defn['desc']}", "", f"**Tickers:** {len(entries)}", "", "---", ""]
    for e in sorted(entries, key=lambda x: x["ticker"]):
        lines.append(f"- **{e['ticker']} {e['company']}** ({e['sector']})")
    return "\n".join(lines)

def main():
    if sys.platform == "win32": sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(THEMES_DIR, exist_ok=True)
    wl_map = scan_wikilinks()
    for tag, defn in THEME_DEFINITIONS.items():
        page = build_theme_page(tag, defn, wl_map)
        if page:
            filename = tag.replace(" ", "_") + ".md"
            with open(os.path.join(THEMES_DIR, filename), "w", encoding="utf-8") as f:
                f.write(page)
            print(f"  Generated theme: {tag}")

if __name__ == "__main__":
    main()
