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

Discover covered tickers affected by completed-day SEC filings:

```bash
python scripts/event_census.py --since 2026-10-01 --through 2026-10-06
python scripts/event_census.py --since 2026-10-01 --through 2026-10-06 --scope universe --output /tmp/us-census.json
```

The census uses SEC daily master indexes plus the SEC CIK/ticker mapping, so it does not make thousands of per-company API calls. It is intentionally a completed-day census: `--through` defaults to the previous UTC date, and the current UTC date is rejected because the daily index is not a real-time completeness source. Current-day publication verification must use SEC submissions.

A missing weekend daily index is treated as an expected no-index day. A missing weekday index remains fail-closed (`complete=false`) until an explicit SEC/exchange calendar adapter proves that date was a non-filing day. This intentionally prefers a false alarm over silently declaring an incomplete census complete.

The census is read-only and fail-closed. `complete=false` means a required source failed and a zero-event result must not be interpreted as "nothing changed."

## R0 boundary

R0 produces an affected-ticker set and deterministic actions such as `refresh_financials`, `check_material_event`, and `revalidate_supply_chain`. It does not bulk-rewrite the coverage database.

The publication gate is claim-scoped. Legacy reports that do not contain verification evidence remain `UNKNOWN` rather than being silently treated as current.
