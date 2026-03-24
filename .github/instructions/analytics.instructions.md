---
applyTo: "backend/analytics/**,**/*.py"
description: "Python analytics conventions for health scoring, RAG classification, and bottleneck detection in the Engineering Delivery Health Analyzer."
---

# Analytics Instructions

## Python Conventions
- snake_case for all names; type hints on every function signature
- Use Pydantic models for input/output, not raw dicts
- Raise `ValueError` for domain errors; let FastAPI routes catch and convert to `HTTPException`

## Data Model
Each issue has these fields:
```python
issue_id: str              # e.g. "PRJA-123", "PRJB2-456", "PRJG3-789"
project:  str              # JIRA project key, e.g. "PRJA", "PRJB2", "PRJG3"
title: str
status: str                # "Open" | "In Progress" | "Blocked" | "Done"
priority: str              # "Low" | "Medium" | "High" | "Critical"
days_open: int             # calendar days since issue was opened
assignee: str              # team member display name
fix_version: str           # e.g. "SITE 14.1", "SITE 14.1 GR", "Unassigned"
fix_version_released: bool # True when the fix version is formally released in JIRA
fix_version_date: str      # ISO date string e.g. "2025-11-14"; empty if unset
space: str                 # logical grouping, e.g. "TSA-SITE", "Voice Policy Engine 2.0"
type: str                  # "Bug" | "Feature" | "Task" | "Improvement"
```

## Spaces and Project Keys

A **Space** maps one or more JIRA project keys to a human-readable product area.
Always filter by `space` when possible — it automatically resolves to the correct project key(s).

| Space | JIRA Project Key |
|---|---|
| `TSA-SITE` | `TSITE` |
| `Voice Policy Engine 2.0` | `VPE2` |
| `RCEM 3.0` | `RCEM3` |
| `AIP Risk Support` | `AIPRS` |

The mapping lives in `_SPACE_TO_PROJECTS` in `backend/analytics/jira_client.py`.

## Health Score Formula
Score is 0–100. Weighted composite:
- **Status weight** (40%): Done=100, In Progress=70, Open=50, Blocked=0
- **Priority weight** (30%): Low=100, Medium=75, High=40, Critical=10
- **Days open weight** (30%): max(0, 100 - days_open * 2)
- Final: `round(0.4 * status_score + 0.3 * priority_score + 0.3 * age_score)`

## RAG Thresholds
- **Green** (≥ 75): On track
- **Amber** (50–74): At risk
- **Red** (< 50): Critical / blocked

## Bottleneck Rules
Thresholds differ by issue **type** (OR logic within each group):

**Bugs** (`type == "Bug"`):
1. `status == "Blocked"` — always flagged
2. `priority == "Critical"` AND `days_open > 5`
3. `status == "In Progress"` AND `days_open > 7`
4. `status == "Open"` AND `days_open > 5`

**Features** (`type == "Feature"`):
1. `status == "Blocked"` — always flagged
2. `priority == "Critical"` AND `days_open > 5`
3. `status == "In Progress"` AND `days_open > 21`
4. `status == "Open"` AND `days_open > 30`

**Tasks / Improvements** (all other types — defaults):
1. `status == "Blocked"` — always flagged
2. `priority == "Critical"` AND `days_open > 5`
3. `status == "In Progress"` AND `days_open > 14`
4. `status == "Open"` AND `days_open > 21`

Sort order: Blocked first, then by `days_open` descending.

## JIRA Integration
- Credentials via env vars: `JIRA_URL`, `JIRA_USER`, `JIRA_API_TOKEN` — never hardcode
- Use `fetch_fix_versions_for_project(project_key, limit=5)` to get top N recent fix versions
- All analytics endpoints accept optional `?project=` and `?fix_version=` query params

## Module Layout
```
analytics/
├── __init__.py
├── scoring.py       # compute_health_score(issue) → int
├── rag.py           # classify_rag(score) → "Red"|"Amber"|"Green"
├── bottlenecks.py   # detect_bottlenecks(issues) → list[Issue]
└── workload.py      # workload_distribution(issues) → dict
```
