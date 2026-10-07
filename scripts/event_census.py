#!/usr/bin/env python3
"""Incremental SEC filing census for US coverage.

R0 is read-only: it discovers affected covered tickers and recommended refresh
actions from SEC daily master indexes. It does not rewrite reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "freshness" / "source_registry.json"
USER_AGENT = "AllenCoverageFreshness/0.1 (source-census; contact via GitHub Allen930311)"
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "8-K", "8-K/A", "20-F", "20-F/A", "40-F", "40-F/A", "6-K", "6-K/A"}


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def source(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    for item in registry["sources"]:
        if item["id"] == source_id:
            return item
    raise KeyError(f"source not registered: {source_id}")


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain,*/*"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def quarter(month: int) -> int:
    return (month - 1) // 3 + 1


def daily_index_url(template: str, day: date) -> str:
    return template.format(year=day.year, quarter=quarter(day.month), yyyymmdd=day.strftime("%Y%m%d"))


def cik_to_tickers(registry: dict[str, Any]) -> dict[str, set[str]]:
    src = source(registry, "sec_company_tickers")
    payload = fetch_json(src["url"])
    mapping: dict[str, set[str]] = {}
    values = payload.values() if isinstance(payload, dict) else payload
    for row in values:
        try:
            cik = str(int(row["cik_str"]))
            ticker = str(row["ticker"]).strip().upper()
        except (KeyError, TypeError, ValueError):
            continue
        if ticker:
            mapping.setdefault(cik, set()).add(ticker)
    return mapping


def covered_tickers() -> set[str]:
    root = ROOT / "Pilot_Reports"
    if not root.exists():
        return set()
    tickers = set()
    for path in root.rglob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        ticker = path.stem.split("_", 1)[0].strip().upper()
        if ticker:
            tickers.add(ticker)
    return tickers


def parse_master_index(text: str) -> list[dict[str, str]]:
    rows = []
    for line in text.splitlines():
        if "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) != 5 or not parts[0].strip().isdigit():
            continue
        cik, company, form, filed, filename = (part.strip() for part in parts)
        rows.append({"cik": str(int(cik)), "company": company, "form": form, "filed": filed, "filename": filename})
    return rows


def actions_for_form(form: str) -> list[str]:
    base = form.replace("/A", "")
    if base in {"10-K", "20-F", "40-F"}:
        return ["refresh_financials", "revalidate_company_profile", "revalidate_supply_chain"]
    if base == "10-Q":
        return ["refresh_financials", "revalidate_supply_chain"]
    if base in {"8-K", "6-K"}:
        return ["check_material_event", "revalidate_claims_if_relevant"]
    return ["review_filing"]


def fingerprint(event: dict[str, Any]) -> str:
    stable = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def daterange(start: date, end: date):
    day = start
    while day <= end:
        yield day
        day += timedelta(days=1)


def validate_window(since: date, through: date, today: date) -> None:
    if through >= today:
        raise ValueError("daily master-index census may only cover completed UTC dates; current-day verification requires SEC submissions")
    if since > through:
        raise ValueError("--since must be on or before --through")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only incremental SEC event census for My-US-Coverage")
    parser.add_argument("--since", help="YYYY-MM-DD. Default: two calendar days ago UTC.")
    parser.add_argument("--through", help="YYYY-MM-DD. Default: previous UTC date; current day is rejected.")
    parser.add_argument("--scope", choices=["covered", "universe"], default="covered")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    through = date.fromisoformat(args.through) if args.through else (now.date() - timedelta(days=1))
    since = date.fromisoformat(args.since) if args.since else (through - timedelta(days=1))
    try:
        validate_window(since, through, now.date())
    except ValueError as exc:
        parser.error(str(exc))
    registry = load_registry()
    src = source(registry, "sec_daily_master_index")

    errors: list[dict[str, str]] = []
    skipped_missing_indexes: list[str] = []
    checked_urls: list[str] = []
    events: list[dict[str, Any]] = []

    try:
        mapping = cik_to_tickers(registry)
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
        mapping = {}
        errors.append({"source_id": "sec_company_tickers", "error": str(exc)})

    covered = covered_tickers()
    for day in daterange(since, through):
        url = daily_index_url(src["url_template"], day)
        try:
            text = fetch_text(url)
            checked_urls.append(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                skipped_missing_indexes.append(day.isoformat())
                continue
            errors.append({"source_id": src["id"], "error": f"{day.isoformat()}: HTTP {exc.code}"})
            continue
        except (urllib.error.URLError, TimeoutError) as exc:
            errors.append({"source_id": src["id"], "error": f"{day.isoformat()}: {exc}"})
            continue

        for row in parse_master_index(text):
            if row["form"] not in FORMS:
                continue
            tickers = sorted(mapping.get(row["cik"], set()))
            if not tickers:
                continue
            for ticker in tickers:
                if args.scope == "covered" and ticker not in covered:
                    continue
                event = {
                    "event_type": "sec_filing",
                    "ticker": ticker,
                    "company": row["company"],
                    "cik": row["cik"],
                    "form": row["form"],
                    "filed_at": row["filed"],
                    "source_id": src["id"],
                    "source_locator": "https://www.sec.gov/Archives/" + row["filename"],
                    "actions": actions_for_form(row["form"]),
                }
                event["fingerprint"] = fingerprint(event)
                events.append(event)

    deduped = {event["fingerprint"]: event for event in events}
    events = sorted(deduped.values(), key=lambda x: (x["filed_at"], x["ticker"], x["form"], x["fingerprint"]))
    affected = sorted({event["ticker"] for event in events})

    payload = {
        "schema_version": "coverage-event-census-v1",
        "market": "US",
        "generated_at": now.isoformat(),
        "since": since.isoformat(),
        "through": through.isoformat(),
        "scope": args.scope,
        "complete": not errors,
        "sources_checked": ["sec_company_tickers", "sec_daily_master_index"] if not errors else ["sec_daily_master_index"],
        "checked_index_count": len(checked_urls),
        "missing_index_dates": skipped_missing_indexes,
        "source_errors": errors,
        "affected_tickers": affected,
        "event_count": len(events),
        "events": events,
    }

    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return 0 if payload["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
