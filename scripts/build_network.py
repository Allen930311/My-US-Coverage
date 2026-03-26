"""
build_network.py — Generate interactive D3.js wikilink network.
"""

import os
import re
import json
import sys
from collections import defaultdict

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "Pilot_Reports")
NETWORK_DIR = os.path.join(os.path.dirname(__file__), "..", "network")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import classify_wikilink

def scan_network():
    nodes = {}
    links = []
    
    for root, dirs, files in os.walk(REPORTS_DIR):
        for f in files:
            if not f.endswith(".md"): continue
            m = re.match(r"^([A-Z0-9\.]+)_(.+)\.md$", f)
            if not m: continue
            ticker, company = m.group(1), m.group(2)
            filepath = os.path.join(root, f)
            
            # Use Ticker as ID for companies
            nodes[ticker] = {"id": ticker, "name": company, "type": "company"}
            
            with open(filepath, "r", encoding="utf-8") as fh:
                content = fh.read()
            
            wikilinks = set(re.findall(r"\[\[([^\]]+)\]\]", content))
            for wl in wikilinks:
                if wl not in nodes:
                    nodes[wl] = {"id": wl, "name": wl, "type": classify_wikilink(wl)}
                links.append({"source": ticker, "target": wl})
                
    return list(nodes.values()), links

def main():
    os.makedirs(NETWORK_DIR, exist_ok=True)
    nodes, links = scan_network()
    data = {"nodes": nodes, "links": links}
    with open(os.path.join(NETWORK_DIR, "network.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Generated network.json: {len(nodes)} nodes, {len(links)} links")

if __name__ == "__main__":
    main()
