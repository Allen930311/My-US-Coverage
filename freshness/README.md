# Coverage Freshness R0

This directory defines the source authority and publication freshness contract for My-US-Coverage.

## Authority

- SEC EDGAR is PRIMARY for filed company facts and disclosures.
- Nasdaq Trader symbol directories are PRIMARY for the listing-symbol census used by this project.
- yfinance is SECONDARY for operational market snapshots and valuation. Filed facts must reconcile to SEC before publication.

## Commands

Audit current report freshness:

```bash
python scripts/freshness.py
python scripts/freshness.py Pilot_Reports/Technology/AAPL_Apple.md --claim supply_chain_claim
```

Discover covered tickers affected by recent SEC filings:

```bash
python scripts/event_census.py --since 2026-10-01
python scripts/event_census.py --since 2026-10-01 --scope universe --output /tmp/us-census.json
```

The census uses SEC daily master indexes plus the SEC CIK/ticker mapping, so it does not make thousands of per-company API calls. Missing weekend/holiday daily indexes are recorded separately from real source failures.

The census is read-only and fail-closed. `complete=false` means a required source failed and a zero-event result must not be interpreted as "nothing changed."

## R0 boundary

R0 produces an affected-ticker set and deterministic actions such as `refresh_financials`, `check_material_event`, and `revalidate_supply_chain`. It does not bulk-rewrite the coverage database.

The publication gate is claim-scoped. Legacy reports that do not contain verification evidence remain `UNKNOWN` rather than being silently treated as current.
