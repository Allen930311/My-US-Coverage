"""
build_wikilink_index.py — Regenerate WIKILINKS.md for US project.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import REPORTS_DIR, is_cjk, TECH_TERMS, MATERIAL_TERMS, APPLICATION_TERMS

OUTPUT_FILE = os.path.join(os.path.dirname(REPORTS_DIR), "WIKILINKS.md")

def collect_wikilinks():
    wikilinks = {}
    for root, dirs, files in os.walk(REPORTS_DIR):
        for f in files:
            if not f.endswith(".md"): continue
            with open(os.path.join(root, f), "r", encoding="utf-8") as fh:
                content = fh.read()
            for wl in re.findall(r"\[\[([^\]]+)\]\]", content):
                wikilinks[wl] = wikilinks.get(wl, 0) + 1
    return wikilinks

def categorize(wikilinks):
    tech, mat, app, us, intl = {}, {}, {}, {}, {}
    for name, count in wikilinks.items():
        if name in TECH_TERMS: tech[name] = count
        elif name in MATERIAL_TERMS: mat[name] = count
        elif name in APPLICATION_TERMS: app[name] = count
        elif not is_cjk(name): us[name] = count
        else: intl[name] = count
    return tech, mat, app, us, intl

def main():
    if sys.platform == "win32": sys.stdout.reconfigure(encoding="utf-8")
    wikilinks = collect_wikilinks()
    tech, mat, app, us, intl = categorize(wikilinks)
    
    lines = ["# US Wikilink Index", "", f"> **{len(wikilinks)}** unique wikilinks. Scaled for US market.", ""]
    
    sections = [("Technologies", tech), ("Materials", mat), ("Applications", app), ("US Companies", us), ("International/CJK", intl)]
    for title, items in sections:
        lines.append(f"## {title} ({len(items)})")
        for name, count in sorted(items.items(), key=lambda x: -x[1])[:100]:
            lines.append(f"- [[{name}]] ({count})")
        lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated WIKILINKS.md: {len(wikilinks)} links")

if __name__ == "__main__":
    main()
