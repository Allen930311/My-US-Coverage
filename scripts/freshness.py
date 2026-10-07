#!/usr/bin/env python3
"""Freshness contract helpers for coverage repositories.

This module is intentionally dependency-free so it can run in CI, Codex,
Claude Code, or a plain Python installation.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "freshness" / "freshness_contract.json"
MARKER_RE = re.compile(
    r"<!--\s*freshness:\s*(?P<domain>[a-z_]+)\s+"
    r"verified_at=(?P<verified_at>\d{4}-\d{2}-\d{2}(?:T[0-9:+\-Z]+)?)\s+"
    r"source=(?P<source>[A-Za-z0-9_.:-]+)\s*-->"
)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
VALUATION_AS_OF_RE = re.compile(r"\bas of\s+(20\d{2}-\d{2}-\d{2})\b", re.IGNORECASE)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if len(raw) == 10:
        raw += "T00:00:00+00:00"
    elif raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def classify_timestamp(
    observed_at: str | None,
    rule: dict[str, Any],
    now: datetime | None = None,
) -> str:
    dt = parse_timestamp(observed_at)
    if dt is None:
        return "UNKNOWN"

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    age_hours = (current - dt).total_seconds() / 3600
    if age_hours < -1:
        return "BLOCKED"

    max_hours = rule.get("max_age_hours")
    if max_hours is None and rule.get("max_age_days") is not None:
        max_hours = float(rule["max_age_days"]) * 24
    if max_hours is None:
        return "UNKNOWN"
    return "FRESH" if age_hours <= float(max_hours) else "STALE"


def extract_markers(content: str) -> dict[str, dict[str, str]]:
    markers: dict[str, dict[str, str]] = {}
    for match in MARKER_RE.finditer(content):
        markers[match.group("domain")] = {
            "verified_at": match.group("verified_at"),
            "source": match.group("source"),
        }
    return markers


def extract_report_observations(content: str) -> dict[str, str | None]:
    markers = extract_markers(content)
    observations: dict[str, str | None] = {}

    valuation_match = VALUATION_AS_OF_RE.search(content)
    observations["valuation"] = valuation_match.group(1) if valuation_match else None

    financial_section = content.split("## 財務概況", 1)[-1] if "## 財務概況" in content else ""
    financial_dates = DATE_RE.findall(financial_section)
    observations["financials"] = max(financial_dates) if financial_dates else None

    for domain in ("company_profile", "supply_chain", "listing_universe", "market_snapshot", "material_events", "monthly_revenue"):
        marker = markers.get(domain)
        observations[domain] = marker["verified_at"] if marker else None
    return observations


def audit_report(path: Path, contract: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    observations = extract_report_observations(content)
    domains = contract["domains"]
    states = {
        domain: classify_timestamp(observations.get(domain), rule, now=now)
        for domain, rule in domains.items()
    }
    return {
        "path": str(path.relative_to(ROOT)),
        "observations": observations,
        "states": states,
    }


def publication_gate(
    states: dict[str, str],
    contract: dict[str, Any],
    claims: list[str] | None = None,
) -> dict[str, Any]:
    required = list(contract["publication_gate"]["always_required"])
    claim_scoped = contract["publication_gate"].get("claim_scoped", {})
    for claim in claims or []:
        required.extend(claim_scoped.get(claim, []))
    required = sorted(set(required))

    allowed = set(contract["publication_gate"].get("allowed_statuses", ["FRESH"]))
    blockers = {
        domain: states.get(domain, "UNKNOWN")
        for domain in required
        if states.get(domain, "UNKNOWN") not in allowed
    }
    return {
        "ready": not blockers,
        "required_domains": required,
        "blockers": blockers,
    }


def discover_reports() -> list[Path]:
    report_root = ROOT / "Pilot_Reports"
    if not report_root.exists():
        return []
    return sorted(
        p for p in report_root.rglob("*.md")
        if p.name.lower() not in {"readme.md"}
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit report freshness against freshness_contract.json")
    parser.add_argument("paths", nargs="*", help="Optional report paths. Defaults to all Pilot_Reports.")
    parser.add_argument("--claim", action="append", default=[], help="Claim type to include in publication gate.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    contract = load_json(CONTRACT_PATH)
    paths = [ROOT / p for p in args.paths] if args.paths else discover_reports()
    audits = [audit_report(path, contract) for path in paths]

    payload = {"schema_version": "freshness-audit-v1", "reports": audits}
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    blocked = 0
    for audit in audits:
        gate = publication_gate(audit["states"], contract, args.claim)
        status = "READY" if gate["ready"] else "BLOCKED"
        if not gate["ready"]:
            blocked += 1
        blockers = ", ".join(f"{k}={v}" for k, v in gate["blockers"].items()) or "-"
        print(f"{status:7} {audit['path']} | {blockers}")

    print(f"\nReports: {len(audits)} | publication-blocked: {blocked}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
