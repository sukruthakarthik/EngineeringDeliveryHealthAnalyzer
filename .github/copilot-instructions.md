# Engineering Delivery Health Analyzer — Workspace Instructions

## Project Context
This is a codathon prototype. A delivery health dashboard that analyzes engineering work items (JIRA-like issues) and surfaces delivery risks, bottleneck patterns, and RAG-based health scores.

## Tech Stack
- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS + Recharts
- **Backend**: Python 3.11 + FastAPI + Uvicorn
- **Data**: JSON mock dataset in `data/issues.json`
- **No database required** — data loaded from file at startup
- **Pinned versions**: `fastapi==0.115.11`, `uvicorn[standard]==0.34.0`, `pydantic==2.10.4`

## Python Environment
The project uses a virtualenv at `venv/` in the repo root. **Always activate it before running any Python or `uvicorn` commands:**
```bash
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Mac/Linux
```
For setup instructions (first-time install, `npm install`, launching both servers), see `.github/prompts/init.prompt.md`.

## Project Structure
```
EngineeringDeliveryHealthAnalyzer/
├── backend/
│   ├── main.py               # FastAPI app entry point; registers all routers
│   ├── requirements.txt      # Pinned Python deps
│   ├── routes/               # One file per domain: health.py, issues.py, bottlenecks.py, workload.py
│   ├── models/               # issue.py (Issue, IssueWithScore, HealthSummary), response.py (make_response)
│   └── analytics/            # data_loader.py, scoring.py, rag.py, bottlenecks.py, workload.py
├── frontend/
│   ├── vite.config.ts        # Vite + React + Tailwind plugins configured
│   ├── src/
│   │   ├── index.css         # @import "tailwindcss" — do not add other global styles
│   │   ├── components/       # React UI components (to be created)
│   │   ├── hooks/            # Custom React hooks for API calls (to be created)
│   │   └── types/            # TypeScript interfaces matching backend models (to be created)
├── data/
│   └── issues.json           # Mock issue dataset (50 items — MUST exist before starting backend)
└── .github/
    ├── copilot-instructions.md
    ├── instructions/          # frontend.instructions.md, analytics.instructions.md, api.instructions.md
    ├── prompts/               # generate-mock-data, health-score-formula, rag-status-component, bottleneck-detection
    └── agents/                # data-analyst.agent.md, dashboard-builder.agent.md
```

## API Endpoints (all prefixed `/api/v1`)

| Method | Path | Returns |
|--------|------|---------|
| GET | `/api/v1/issues` | All raw issues wrapped in response envelope |
| GET | `/api/v1/health-score` | `HealthSummary` with per-issue scores + bottleneck flags |
| GET | `/api/v1/health-score/by-release` | `ReleaseHealth[]` grouped by fix version; params: `space`, `limit` |
| GET | `/api/v1/bottlenecks` | Sorted list of bottleneck `IssueWithScore` items |
| GET | `/api/v1/workload` | `{ Critical: n, High: n, Medium: n, Low: n }` (active issues only) |
| GET | `/api/v1/jira/spaces` | Known spaces and their JIRA project keys |
| GET | `/api/v1/jira/sync` | Sync issues from JIRA; params: `space` (preferred) or `project`, `fix_version`, `assignee`, `max_results` |
| GET | `/api/v1/jira/projects` | All JIRA projects visible to the configured credentials |
| GET | `/api/v1/jira/fix-versions` | Fix versions for a project; params: `project`, `limit` |
| GET | `/api/v1/jira/users` | Assignable users for a project; params: `project` |
| GET | `/` | `{ "message": "Engineering Delivery Health Analyzer API" }` |

Interactive docs: `http://localhost:8000/docs`

## Data Schema (`data/issues.json`)

Each item must match the `Issue` Pydantic model exactly:
```json
{
  "issue_id": "TSITE-12413",
  "title": "string",
  "project": "TSITE | VPE2 | RCEM3 | RCEM32",
  "status": "Open | In Progress | Blocked | Done",
  "priority": "Low | Medium | High | Critical",
  "days_open": 14,
  "assignee": "Display Name",
  "fix_version": "SITE 14.1 | SITE 14.1 GR | SITE 14.1 TMO | Unassigned",
  "fix_version_released": false,
  "fix_version_date": "2025-11-14",
  "space": "TSA-SITE | Voice Policy Engine 2.0 | RCEM 3.0 | RCEM 3.2",
  "type": "Bug | Feature | Task | Improvement"
}
```

## Space → Project Mapping

A **Space** is the product-area label that maps to one or more JIRA project keys.
Always use `space` when filtering — it resolves to the correct project key(s) automatically.

| Space | JIRA Project Key |
|---|---|
| `TSA-SITE` | `TSITE` |
| `Voice Policy Engine 2.0` | `VPE2` |
| `RCEM 3.0` | `RCEM3` |
| `RCEM 3.2` | `RCEM32` |

Mapping defined in `_SPACE_TO_PROJECTS` in `backend/analytics/jira_client.py`.  
Use `GET /api/v1/jira/spaces` to retrieve the mapping at runtime.

## Scoring & RAG Logic

**Health score formula** (0–100, per issue):
```
score = 0.4 × status_score + 0.3 × priority_score + 0.3 × age_score
age_score = max(0, 100 - days_open × 2)
```
Status scores: `Done=100, In Progress=70, Open=50, Blocked=0`  
Priority scores: `Low=100, Medium=75, High=40, Critical=10`

**RAG thresholds**: Green ≥ 75 · Amber 50–74 · Red < 50  
**Team score**: average health score of all non-Done issues (100 if none active)

**Bottleneck rules** (OR logic, thresholds differ by type):
- **Bug**: Blocked | Critical > 5d | In Progress > 7d | Open > 5d
- **Feature**: Blocked | Critical > 5d | In Progress > 21d | Open > 30d
- **Task/Improvement** (default): Blocked | Critical > 5d | In Progress > 14d | Open > 21d

Sort order: Blocked first, then by `days_open` descending.

## Response Envelope

Every API response uses `make_response()` from `models/response.py`:
```json
{
  "data": "<payload>",
  "meta": { "generated_at": "2026-03-13T10:00:00+00:00" }
}
```
Never return raw dicts directly from route handlers — always wrap with `make_response()`.

## Assumptions (documented)
1. Mock data is acceptable — no live JIRA/ADO connection required
2. No authentication or multi-tenancy — single-team prototype
3. Health score formula: weighted composite of status, priority, and days_open
4. RAG thresholds: Red < 50, Amber 50–74, Green ≥ 75 (out of 100)
5. "Blocked" and "Critical" items are always treated as high-risk regardless of days_open
6. Workload distribution is by priority bucket (not by assignee — no PII in mock data)

## Coding Conventions
- Python: snake_case, type hints on all function signatures, Pydantic for request/response models
- TypeScript: PascalCase for components, camelCase for variables, no `any` types
- All API responses use a consistent envelope: `{ data: ..., meta: { generated_at: ... } }`
- Error handling: FastAPI HTTPException with descriptive messages
- Keep components small — max ~100 lines per component file
- Frontend components use Tailwind utility classes only — no custom CSS, no inline styles
- Recharts charts must be wrapped in `<ResponsiveContainer>` for responsive layout
- RAG colors: Red `#ef4444` · Amber `#f59e0b` · Green `#22c55e`

## Key Pitfalls
- `load_issues()` uses `@lru_cache` — **restart the backend** to pick up changes to `data/issues.json`
- CORS is configured for `http://localhost:5173` only — do not change the Vite port without updating `main.py`
- All routers use the `/api/v1` prefix — do not call bare paths like `/health-score` from the frontend
- `_is_bottleneck()` is a private function; routes import it directly — avoid adding public aliases

## GitHub Copilot Usage Notes
- Use `/generate-mock-data` to create or extend the issue dataset
- Use `/health-score-formula` to reason about scoring weights
- Use `/rag-status-component` to build or modify RAG visualization
- Use `/bottleneck-detection` to implement or adjust bottleneck logic
- Use the `data-analyst` agent for backend/analytics work
- Use the `dashboard-builder` agent for frontend/UI work

## Documentation Maintenance
Whenever a new requirement is introduced or an existing one changes, **always update all relevant documentation files** before finishing:

| Changed area | Files to update |
|---|---|
| New or modified API endpoint | `docs/API_REFERENCE.md` and the API Endpoints table in this file |
| New/changed data field | `docs/API_REFERENCE.md` field reference tables, `data/issues.json` schema in this file, `analytics.instructions.md` data model section |
| New space or project key | Space → Project Mapping table in this file, `analytics.instructions.md`, `jira-sync` SKILL, `API_REFERENCE.md` examples |
| Scoring/RAG/bottleneck rule change | `health-scoring` SKILL, Scoring & RAG Logic in this file, `analytics.instructions.md` |
| JIRA mapping change (status/priority/type) | `jira-sync` SKILL |

This keeps all documentation in sync with the codebase and prevents stale instructions from misleading Copilot or team members.
