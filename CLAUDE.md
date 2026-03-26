# My-US-Coverage CLI & Quality Guide

## Core Commands

### Report Management
- **Add Ticker**: `python scripts/add_ticker.py <ticker> <name>`
  - Example: `python scripts/add_ticker.py AAPL Apple`
- **Update Financials**: `python scripts/update_financials.py <ticker_or_scope>`
  - Example: `python scripts/update_financials.py --all`
- **Update Valuation**: `python scripts/update_valuation.py <ticker>`
- **Apply Enrichment**: `python scripts/update_enrichment.py <ticker> <json_file>`

### Analysis & Audit
- **Audit Quality**: `python scripts/audit_batch.py <batch_num> [-v]`
- **Build Index**: `python scripts/build_wikilink_index.py`
- **Build Themes**: `python scripts/build_themes.py`
- **Build Network**: `python scripts/build_network.py`

## Quality Standards (Golden Rules)

1. **Language**:
   - **Reports Titles**: `Ticker_Name.md` (e.g., `AAPL_Apple.md`).
   - **Content**: All business descriptions and supply chain analysis must be in **Traditional Chinese**.
   - **Wikilinks**: Use **English canonical names** for companies (e.g., `[[NVIDIA]]`, NOT `[[輝達]]`).

2. **Wikilink Graph**:
   - Every report must have **10+ wikilinks**.
   - **Strict Real-Name Policy**: Avoid generic terms like `[[大廠]]` or `[[供應商]]`. Always use specific company names or technology standards.
   - **Cross-Linking**: Link to technologies (e.g., `[[CoWoS]]`, `[[HBM]]`), materials (e.g., `[[SiC]]`), and applications (e.g., `[[AI Server]]`).

3. **Financial Data**:
   - Units: **Million USD**.
   - Margins: **%**.
   - Valuation multiples should be refreshed regularly via `update_valuation.py`.

4. **Directory Structure**:
   - Organize reports by **Sector** (auto-detected from yfinance).
   - Folders should be named after GICS or standard industry classifications.
