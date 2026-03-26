# My-US-Coverage

An equity research database for all US-listed companies (NYSE, NASDAQ, AMEX), modeled after the My-TW-Coverage project.

## Features
- **6,500+ Tickers Coverage**: Full market support.
- **Wikilink Knowledge Graph**: Deep mapping of US tech and supply chain relationships.
- **Automated Financials**: 3-year annual and 4-quarterly data in USD.
- **Thematic Analysis**: Supply chain maps for AI, EV, SaaS, and more.
- **Interactive Visualization**: D3.js network graph of the US market players.

## Project Structure
- `Pilot_Reports/`: Markdown research reports categorized by sector.
- `scripts/`: Automation tools for data fetching and enrichment.
- `themes/`: Thematic investment screens.
- `network/`: Graph visualization data.
- `tickers_us.csv`: Master list of US symbols.

## Quick Start
1. Ensure `yfinance` and `pandas` are installed.
2. Generate a new report: `python scripts/add_ticker.py AAPL Apple`.
3. Enrich with AI content using the `update_enrichment.py` tool.
4. Audit quality: `python scripts/audit_batch.py --all`.
