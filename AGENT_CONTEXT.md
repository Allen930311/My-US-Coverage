# AGENT_CONTEXT — My-US-Coverage

> Fresh-agent entrypoint. Reconciled 2026-10-08.

## What this repo is

US-listed equity-coverage research database with generated company reports,
financial snapshots, enrichment and relationship/knowledge-graph material.

## Critical freshness boundary

This repository contains valuable **research coverage**, but the existing report
corpus and old batch checklist do **not** prove that market/company facts are
fresh today.

Do not use an old generated report as current investment truth without
revalidating its source timestamp and the fields relevant to the decision.

## Authority

| Concern | Source |
|---|---|
| Repository purpose / commands / data layout | `README.md` |
| Historical build coverage / old batch completion | `task.md` |
| Company report content | exact file under `Pilot_Reports/` |
| Current market/company facts | fresh source evidence collected for the current task; never inferred from report age |

`task.md` is a build-progress ledger, **not** a live market-freshness
authority.

## Current gate

The next system concern is to establish a durable **Source Registry + Freshness
Contract + Incremental Update / Event Census** so agents can distinguish:
- structural/static company knowledge;
- periodically refreshable financial data;
- event-driven company changes;
- stale/unknown fields.

Until that exists, fail closed on freshness-sensitive conclusions.

## Remote vs local truth

Remote default branch is shared repository state. Local caches, notebooks,
uncommitted refresh output and machine-specific data are not shared truth.

## Planning / implementation boundary

A fresh agent may inspect, audit freshness, and propose the smallest update path.
Do not bulk-refresh the entire market, overwrite research, or redesign the
coverage model merely because data may be old unless the current task authorizes
that scope.

## Safe start

1. Read `README.md`.
2. Treat `task.md` as historical build progress.
3. Identify which facts in the user's question are freshness-sensitive.
4. Revalidate only the necessary facts/sources before analysis.
5. Preserve provenance and USD data semantics when updating.
