# Engineering Delivery Health Analyzer

## Presentation Outline

---

## Slide 1 — Title

**Engineering Delivery Health Analyzer**
Real-time delivery risk and workload visibility for engineering teams

- Codathon Prototype
- Built with: React + FastAPI + JIRA Integration
- Team: Sukrutha Karthik, Roja Rameti, Sumit Kumar, Bruno Ferraz, Chandramouli B

---

## Slide 2 — Problem Statement

### The Challenge

Engineering teams struggle with:

- **No single view** of delivery health across multiple products/releases
- **Manual risk identification** — bottlenecks are found too late in the cycle
- **Scattered data** — JIRA issues spread across projects with no unified health metric
- **Reactive decision-making** — teams learn about blockers only in standup meetings
- **No quantified risk** — "How healthy is our release?" has no objective answer

### Impact

- Delayed releases due to undetected blockers
- Wasted time in status meetings gathering information manually
- Inconsistent risk assessment across different project leads

---

## Slide 3 — Solution Overview

### Engineering Delivery Health Analyzer

A **real-time dashboard** that:

1. **Syncs live data from JIRA** across multiple projects
2. **Computes a health score (0–100)** for every issue using a weighted formula
3. **Classifies issues into RAG status** (Red / Amber / Green)
4. **Automatically detects bottlenecks** using type-aware stale thresholds
5. **Aggregates team-level health** per release version
6. **Visualizes workload distribution** by priority

### Key Value Proposition

> "Replace guesswork with data-driven delivery health visibility — in real time."

---

## Slide 4 — Architecture Overview

### System Architecture

```
┌─────────────────────────┐   REST API (JSON)   ┌─────────────────────────┐         ┌──────────────────┐
│        FRONTEND         │                     │         BACKEND         │         │ data/issues.json │
│  React + TypeScript     │ ──────────────────► │  FastAPI + Uvicorn      │ ──────► │   (local cache)  │
│  Tailwind + Recharts    │                     │  Python 3.11 + Pydantic │         └──────────────────┘
│  Vite (localhost:5173)  │                     │  localhost:8000         │
│                         │                     │                         │         ┌──────────────────┐
│  ┌───────────────────┐  │                     │  ┌───────────────────┐  │         │   JIRA Cloud     │
│  │ Landing Page      │  │                     │  │ Routes (5 files)  │  │ ──────► │   REST API v3    │
│  ├───────────────────┤  │                     │  ├───────────────────┤  │         │   (Live data)    │
│  │ Dashboard         │  │                     │  │ Analytics Engine  │  │         └──────────────────┘
│  ├───────────────────┤  │                     │  ├───────────────────┤  │
│  │ Charts & Tables   │  │                     │  │ JIRA Client       │  │
│  └───────────────────┘  │                     │  └───────────────────┘  │
└─────────────────────────┘                     └─────────────────────────┘
```

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React + TypeScript | 18.3.1 + TS 5.7 |
| Styling | Tailwind CSS | 3.4.17 |
| Charts | Recharts | 2.14.1 |
| Bundler | Vite | 6.2.0 |
| Backend | FastAPI + Uvicorn | 0.115.11 + 0.34.0 |
| Data Models | Pydantic | 2.10.4 |
| JIRA Integration | Requests + python-dotenv | 2.32.3 + 1.0.1 |

---

## Slide 5 — Data Flow & JIRA Integration

### Live JIRA Sync Pipeline

```
JIRA Cloud API ──► jira_client.py ──► Normalize & Map ──► issues.json ──► Analytics Engine
     │                                      │
     │  - fetch_issues()                    │  Status mapping (20+ statuses → 4)
     │  - fetch_fix_versions()              │  Priority mapping (10+ levels → 4)
     │  - fetch_active_release()            │  Type mapping (15+ types → 4)
     │  - fetch_users()                     │  Days-open calculation
     └─────────────────────────────────────-┘
```

### Multi-Project Support

| Space (Product Area) | JIRA Project Key | Team Lead |
|---|---|---|
| TSA-SITE | TSITE | Sukrutha Karthik |
| Voice Policy Engine 2.0 | VPE2 | Roja Rameti |
| RCEM 3.0 | RCEM3 | Sumit Kumar |
| AIP Risk Support | AIPRS | Bruno Ferraz |
| Steering 9.0 | NTR9 | Chandramouli B |

### JIRA Field Normalization

**Status mapping** (20+ JIRA statuses → 4 internal statuses):

| JIRA Status | Internal Status |
|---|---|
| Open, Estimation Request, In Planning, To Do, Backlog, Reopened | **Open** |
| In Development, In Progress, In Review, In Testing, L3 Analysis | **In Progress** |
| Information Provided, Blocked, On Hold, Impediment | **Blocked** |
| Fixed, Closed, Resolved, Released, Done, Rejected, Withdrawn | **Done** |

**Priority mapping** (JIRA → Internal):

| JIRA Priority | Internal Priority |
|---|---|
| 1-Blocker, Highest, Critical, Blocker | **Critical** |
| 2-High, High | **High** |
| 3-Medium, Medium, Normal | **Medium** |
| 5-Very Low, Low, Lowest, Trivial, 4-Low | **Low** |

**Issue Type mapping** (JIRA → Internal):

| JIRA Type | Internal Type |
|---|---|
| General Testing Defect, External Defect, QE Defect, Bug | **Bug** |
| Story, Epic, Feature, New Feature | **Feature** |
| Task, Sub-task, SW Release, Tracking Item | **Task** |
| Documentation, Improvement, Enhancement | **Improvement** |

---

## Slide 6 — Health Score Algorithm

### Weighted Composite Score (0–100)

```
Health Score = 0.4 × Status Score + 0.3 × Priority Score + 0.3 × Age Score
```

#### Status Component (40% weight)

| Status | Score | Rationale |
|---|---|---|
| Done | 100 | Completed — no risk |
| In Progress | 70 | Actively being worked on |
| Open | 50 | Not started — moderate risk |
| Blocked | 0 | Cannot proceed — maximum risk |

#### Priority Component (30% weight)

| Priority | Score | Rationale |
|---|---|---|
| Low | 100 | Minimal impact if delayed |
| Medium | 75 | Standard work items |
| High | 40 | Significant impact — needs attention |
| Critical | 10 | Showstopper — urgent resolution needed |

#### Age Component (30% weight) — Type-Aware Decay

```
Age Score = max(0, 100 − days_open × decay_rate)
```

| Issue Type | Decay Rate | Days to reach 0 | Rationale |
|---|---|---|---|
| Bug | 7.0 | ~14 days | Defects must be fixed fast in testing cycles |
| Task | 3.0 | ~33 days | Should close within a sprint |
| Improvement | 2.0 | ~50 days | Medium-term work |
| Feature | 1.0 | ~100 days | Can span a full release cycle |

### Example Calculations

| Issue | Status | Priority | Days Open | Type | Score |
|---|---|---|---|---|---|
| Critical Blocked Bug | Blocked (0) | Critical (10) | 30 | Bug (0) | **3** 🔴 |
| Medium In-Progress Task | In Progress (70) | Medium (75) | 10 | Task (70) | **72** 🟡 |
| Low Done Feature | Done (100) | Low (100) | 60 | Feature (40) | **82** 🟢 |

---

## Slide 7 — RAG Classification & Team Score

### RAG (Red / Amber / Green) Thresholds

| RAG Status | Score Range | Meaning | Action Required |
|---|---|---|---|
| 🟢 Green | ≥ 75 | Healthy — on track | Continue monitoring |
| 🟡 Amber | 50 – 74 | At risk — needs attention | Investigate and plan mitigation |
| 🔴 Red | < 50 | Critical — immediate action | Escalate and resolve blockers |

### Team Health Score

The **team score** is the average health score of all **non-Done** (active) issues:

```
Team Score = Σ(health_score of active issues) / count(active issues)
```

- If all issues are Done → Team Score = 100
- Only active issues (Open, In Progress, Blocked) count
- One Blocked Critical issue can drag the entire team score into Red

### RAG Color Palette (consistent across all visualizations)

| Color | Hex Code | Tailwind Class |
|---|---|---|
| Red | `#ef4444` | `bg-red-500` |
| Amber | `#f59e0b` | `bg-amber-400` |
| Green | `#22c55e` | `bg-green-500` |

---

## Slide 8 — Bottleneck Detection Engine

### Automatic Risk Flagging

Issues are flagged as bottlenecks when **any one** of these conditions is true (OR logic):

#### Thresholds by Issue Type

| Condition | Bug | Feature | Task / Improvement |
|---|---|---|---|
| Status = Blocked | ✅ Always | ✅ Always | ✅ Always |
| Priority = Critical AND days > 5 | ✅ | ✅ | ✅ |
| In Progress AND days > N | > 7 days | > 21 days | > 14 days |
| Open AND days > N | > 5 days | > 30 days | > 21 days |

> Bugs have the tightest thresholds — a bug open for 6 days is already flagged.
> Features have the loosest — they legitimately span multiple sprints.

### Bottleneck Sort Order

1. **Blocked issues first** (highest severity)
2. **Then by `days_open` descending** (longest-stuck items surface to the top)

### Bottleneck Reasons (human-readable)

Each bottleneck includes a reason string:
- `"Blocked status"` — issue is stuck
- `"Critical priority open for 45 days"` — urgent item aging
- `"Bug in progress for 12 days (stale after 7d)"` — exceeded type threshold
- `"Task open for 25 days (overdue after 21d)"` — unstarted too long

---

## Slide 9 — API Design

### RESTful JSON API — All endpoints under `/api/v1`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/issues` | All issues with optional filters |
| GET | `/api/v1/health-score` | Team health score + per-issue scores |
| GET | `/api/v1/health-score/by-release` | Health grouped by fix version |
| GET | `/api/v1/bottlenecks` | Flagged bottleneck issues |
| GET | `/api/v1/workload` | Priority distribution (active issues) |
| GET | `/api/v1/jira/spaces` | Available product spaces |
| GET | `/api/v1/jira/sync` | Live JIRA sync → updates local data |
| GET | `/api/v1/jira/fix-versions` | Fix versions for a project |
| GET | `/api/v1/jira/active-release` | Current unreleased version |
| GET | `/api/v1/jira/users` | Assignable users for a project |
| GET | `/api/v1/jira/projects` | All visible JIRA projects |

### Consistent Response Envelope

Every API response wrapped in a standard envelope:

```json
{
  "data": { ... },
  "meta": {
    "generated_at": "2026-03-19T10:30:00+00:00"
  }
}
```

### Query Parameters

All dashboard endpoints support `?project=TSITE` filtering to scope results per product area.

---

## Slide 10 — Frontend: Landing Page

### Multi-Space Overview

The landing page shows **all product spaces as cards**, each with:

- **Space name** (e.g., "TSA-SITE")
- **Active release badge** (fetched from JIRA API — the current unreleased version)
- **RAG donut chart** — PieChart showing Red/Amber/Green distribution for active release
- **Issue counts** — Red, Amber, Green breakdown
- **Team lead** — assigned contributor chip
- **"View Details" button** — navigates to the full dashboard for that space

### Key Design Decisions

- Each card independently fetches its own health data (parallel API calls)
- Cards auto-detect the active release from JIRA and filter to it
- If no active release exists, shows all issues under "Internal" label
- Responsive grid: 1 column (mobile) → 2 columns (tablet) → 3 columns (desktop)

---

## Slide 11 — Frontend: Dashboard View

### Per-Space Dashboard Components

When a user clicks "View Details" on a space card, they enter the full dashboard:

#### 1. Header Section
- **Home button** — returns to landing page
- **Space indicator** — "Current Space: TSA-SITE"
- **Release version dropdown** — switch between fix versions (fetched from JIRA)
- **Active/Completed badge** — shows if the selected release is still in progress or completed
- **Live data indicator** — auto-refresh every 5 minutes
- **Export buttons** — Print, CSV export, JSON export

#### 2. Filter Bar
- **Multi-select dropdowns** for: Status, Priority, Health (RAG)
- **Active filter chips** — visual indicators of applied filters
- **Filter counter** — "12 of 74" showing filtered vs. total issues
- **Clear all** — one-click filter reset

#### 3. Health Score Card
- **Large circular gauge** — team score (0–100) with RAG-colored border
- **RAG badge** — Green / Amber / Red status label
- **Issue summary** — "74 total · 12 active"
- **Legend** — explains RAG thresholds

#### 4. Workload Distribution Chart
- **Bar chart** (Recharts `BarChart`) — Critical / High / Medium / Low priority counts
- Only counts **active issues** (excludes Done)
- Priority bars change color based on filter selection (greyed out if filtered out)
- Shows "Release completed" state for historical releases

#### 5. Bottleneck Table
- **Sortable table** listing all flagged bottleneck issues
- Columns: ID, Title, Status, Priority, Days Open, Score, RAG, Reason
- **Status/Priority badges** with color coding
- **Bottleneck count badge** in header
- For completed releases: shows "Retrospective Bottleneck Analyzer with AI — Coming soon" teaser

---

## Slide 12 — Frontend: Technical Implementation

### Component Architecture

```
App.tsx (State Manager)
├── LandingPage.tsx
│   └── SpaceCard.tsx (per-space card with mini PieChart)
└── Dashboard View
    ├── Filters.tsx (multi-select dropdowns with chips)
    ├── HealthScoreCard.tsx (circular gauge + RAG badge)
    ├── WorkloadDistribution.tsx (BarChart by priority)
    ├── BottleneckTable.tsx (sorted risk table)
    └── ExportPrintButtons.tsx (Print + CSV + JSON)
```

### Custom React Hooks (Data Layer)

| Hook | Endpoint | Purpose |
|---|---|---|
| `useHealthScore(space?)` | `/api/v1/health-score` | Team score + per-issue data |
| `useBottlenecks(space?, fixVersion?)` | `/api/v1/bottlenecks` | Bottleneck issue list |
| `useWorkload(space?)` | `/api/v1/workload` | Priority distribution |
| `useSpaces()` | `/api/v1/jira/spaces` | Available product spaces |
| `useFixVersions(space?)` | `/api/v1/jira/fix-versions` | Release version list |
| `useActiveRelease(space?)` | `/api/v1/jira/active-release` | Current unreleased version |
| `useIssues(space?)` | `/api/v1/issues` | Raw issue list |

### All hooks follow the same pattern:
- Return `{ data, loading, error }` state
- Auto-refresh every 5 minutes
- Resolve space names to JIRA project IDs via `projectMapping.ts`
- Type-safe with TypeScript generics

### Client-Side Filtering

Filters (Status, Priority, RAG) are applied **client-side** on the already-fetched data:
- Avoids extra API calls for every filter change
- Team score is recomputed dynamically based on filtered issues
- Bottlenecks are filtered in sync with the main health data

---

## Slide 13 — Backend: Module Structure

### Clean Separation of Concerns

```
backend/
├── main.py                     # FastAPI app creation, CORS, router registration
├── requirements.txt            # Pinned dependencies (5 packages)
│
├── models/                     # Pydantic data models
│   ├── issue.py                # Issue, IssueWithScore, HealthSummary, ReleaseHealth
│   └── response.py             # make_response() envelope helper
│
├── routes/                     # API endpoint handlers (one per domain)
│   ├── issues.py               # GET /api/v1/issues
│   ├── health.py               # GET /api/v1/health-score, /health-score/by-release
│   ├── bottlenecks.py          # GET /api/v1/bottlenecks
│   ├── workload.py             # GET /api/v1/workload
│   └── jira.py                 # GET /api/v1/jira/* (spaces, sync, versions, users)
│
├── analytics/                  # Pure business logic (no HTTP concerns)
│   ├── scoring.py              # compute_health_score(), compute_team_score()
│   ├── rag.py                  # classify_rag() → "Red" | "Amber" | "Green"
│   ├── bottlenecks.py          # detect_bottlenecks(), bottleneck_reason()
│   ├── workload.py             # workload_distribution()
│   ├── data_loader.py          # load_issues() with @lru_cache
│   └── jira_client.py          # JIRA API integration (sync, versions, users)
│
└── utils/
    └── project_mapping.py      # Space ↔ Project ID bidirectional mapping
```

### Key Design Patterns

- **Pydantic models** for all data structures — automatic validation and serialization
- **`@lru_cache`** on `load_issues()` — data loaded once, cached in memory until restart or sync
- **Response envelope** via `make_response()` — consistent `{ data, meta }` wrapper
- **Analytics engine is HTTP-agnostic** — pure functions that can be unit tested independently
- **Router separation** — each domain has its own file, mounted in `main.py`

---

## Slide 14 — Data Model

### Core Issue Schema

```json
{
  "issue_id": "TSITE-12413",
  "title": "TMO TACC R1/2026: user settings mangled",
  "project": "TSITE",
  "status": "In Progress",
  "priority": "Medium",
  "days_open": 9,
  "assignee": "Sukrutha Karthik",
  "fix_version": "SITE 14.1 TMO",
  "fix_version_released": false,
  "fix_version_date": "2025-11-14",
  "space": "TSA-SITE",
  "type": "Bug"
}
```

### Extended Models

**IssueWithScore** (Issue + analytics):
```
+ health_score: int (0–100)
+ rag: "Red" | "Amber" | "Green"
+ bottleneck: bool
+ bottleneck_reason: string | null
```

**HealthSummary** (team aggregate):
```
+ team_score: int (0–100)
+ rag: "Red" | "Amber" | "Green"
+ total_issues: int
+ issues: IssueWithScore[]
```

**ReleaseHealth** (per fix-version aggregate):
```
+ fix_version, fix_version_date, released, space
+ score, rag
+ total/open/in_progress/blocked/done issues
+ bottleneck_count
```

---

## Slide 15 — JIRA Sync Mechanism

### Sync Workflow

```
User clicks "Sync" (or API call)
         │
         ▼
GET /api/v1/jira/sync?project=TSITE&fix_version=SITE+14.1
         │
         ▼
┌─────────────────────────────────────────────┐
│ jira_client.fetch_issues()                  │
│  1. Build JQL query                          │
│  2. Paginate through JIRA API (100 per page)│
│  3. Normalize each issue's fields            │
│  4. Calculate days_open from created date    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Merge Strategy                               │
│  1. Load existing issues.json                │
│  2. Remove all issues for synced project     │
│  3. Append freshly fetched issues            │
│  4. Write merged data back to file           │
│  5. Clear @lru_cache so API uses fresh data  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
Response: { "synced": 74, "total_in_file": 250, "project": "TSITE" }
```

### JIRA API Endpoints Used

| JIRA API | Our Wrapper | Purpose |
|---|---|---|
| `GET /rest/api/3/search/jql` | `fetch_issues()` | Search issues with JQL |
| `GET /rest/api/3/project/{key}/versions` | `fetch_fix_versions_for_project()` | Get release versions |
| `GET /rest/api/3/project/{key}/versions` | `fetch_active_release()` | Find current unreleased version |
| `GET /rest/api/3/user/assignable/search` | `fetch_users_for_project()` | Get team members |
| `GET /rest/api/3/project/search` | `fetch_projects()` | List all projects |

### Security

- Credentials via **environment variables** (`JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`)
- Loaded from `.env` file using `python-dotenv`
- **Never hardcoded** — `.env` is in `.gitignore`
- HTTP Basic Auth for JIRA Cloud API
- CORS restricted to `localhost:5173` (Vite dev server)

---

## Slide 16 — Export & Print Capabilities

### Three Export Formats

| Format | Description |
|---|---|
| **Print** | Browser print dialog — dashboard styled for print via `print:hidden` Tailwind classes |
| **CSV** | All visible issues exported with all fields (ID, Title, Status, Priority, Score, RAG, etc.) |
| **JSON** | Full issue data as formatted JSON — useful for further analysis |

### Export Scope

- Exports respect all active filters (status, priority, RAG)
- Filename includes the space name: `dashboard-TSA-SITE.csv`
- Print mode hides interactive elements (buttons, filters) automatically

---

## Slide 17 — Key Features Summary

| Feature | Description |
|---|---|
| 🏠 **Multi-Space Landing Page** | Overview cards for all product areas with RAG distribution |
| 📊 **Health Score Engine** | Weighted composite score (status + priority + age) per issue |
| 🚦 **RAG Classification** | Automatic Red/Amber/Green based on score thresholds |
| 🚧 **Bottleneck Detection** | Type-aware stale thresholds with human-readable reasons |
| 📈 **Workload Distribution** | Active issues by priority — visual bar chart |
| 🔄 **Live JIRA Sync** | Pull real data from JIRA Cloud with full field normalization |
| 🏷️ **Release-Aware** | Auto-detects active release, supports switching between versions |
| 🔍 **Multi-Filter Dashboard** | Status, Priority, Health filters with chip indicators |
| 📤 **Export (CSV/JSON/Print)** | Dashboard data exportable in multiple formats |
| ⏱️ **Auto-Refresh** | Data refreshes every 5 minutes automatically |
| 📱 **Responsive Design** | Tailwind-powered responsive layout (mobile → desktop) |

---

## Slide 18 — AI-Assisted Development

### Built with GitHub Copilot as Co-Developer

The entire project was built using **AI-assisted development** with GitHub Copilot, leveraging:

#### Custom Copilot Configuration

| Artifact | Purpose |
|---|---|
| `copilot-instructions.md` | Global project context, conventions, and architecture rules |
| `analytics.instructions.md` | Python conventions for scoring, RAG, and bottleneck logic |
| `api.instructions.md` | FastAPI route and model conventions |
| `frontend.instructions.md` | React + TypeScript + Tailwind coding standards |
| `project-name-mapping.instructions.md` | Space ↔ Project ID mappings |

#### Custom Skills

| Skill | Domain |
|---|---|
| `health-scoring` | Modifying scoring weights, RAG thresholds, bottleneck rules |
| `jira-sync` | JIRA field mappings, sync logic, data pipeline |

#### Specialized Agents

| Agent | Expertise |
|---|---|
| `data-analyst` | Backend analytics: health scores, bottlenecks, FastAPI endpoints |
| `dashboard-builder` | Frontend UI: React components, Recharts, API hooks |

#### Custom Prompts

| Prompt | Purpose |
|---|---|
| `generate-mock-data` | Create/extend the issue dataset |
| `health-score-formula` | Reason about scoring weights |
| `rag-status-component` | Build RAG visualization components |
| `bottleneck-detection` | Implement bottleneck detection logic |

### Impact of AI-Assisted Development

- **Rapid prototyping** — from concept to working dashboard in record time
- **Consistent code quality** — enforced via instruction files and coding conventions
- **Domain knowledge preservation** — captured in skills and instruction files
- **Reduced context switching** — specialized agents handle backend vs. frontend work

---

## Slide 19 — Future Roadmap

### Planned Enhancements

| Feature | Description |
|---|---|
| 🤖 **AI Retrospective Analyzer** | AI-powered insights for completed releases — pattern detection across historical data |
| 📊 **Trend Charts** | Health score trends over time — track improvement or degradation |
| 👥 **Assignee-Level View** | Per-developer workload and health metrics |
| 🔔 **Alert Notifications** | Slack/Teams alerts when issues transition to Red or become bottlenecks |
| 📋 **Sprint Velocity Tracking** | Story points completed vs. planned per sprint |
| 🔗 **ADO Integration** | Azure DevOps support alongside JIRA |
| 🔐 **Authentication** | Multi-tenant support with team-based access control |
| 📈 **Custom Dashboards** | Configurable widgets and layout per user |

---

## Slide 20 — Demo Walkthrough

### Live Demo Flow

1. **Landing Page** → Show all 5 product spaces with RAG donut charts
2. **Click "TSA-SITE"** → Enter dashboard with active release auto-selected
3. **Health Score Card** → Team score with RAG gauge
4. **Workload Chart** → Priority distribution bars
5. **Bottleneck Table** → Blocked and stale issues sorted by severity
6. **Apply Filters** → Filter by Status = "Blocked", see score change dynamically
7. **Switch Release** → Dropdown to a completed release, show historical view
8. **Export CSV** → Download filtered data
9. **Return Home** → Navigate back to multi-space overview

---

## Slide 21 — Technical Highlights

### What Makes This Special

1. **Type-aware scoring** — Bugs decay 7× faster than Features, reflecting real-world urgency
2. **Zero-config JIRA normalization** — 20+ JIRA statuses mapped to 4 clean categories automatically
3. **Client-side filtering** — No extra API calls when toggling filters; instant response
4. **Merge-on-sync** — JIRA sync replaces only the synced project's data, preserving other projects
5. **Cache-aware data loading** — `@lru_cache` for performance; `cache_clear()` after JIRA sync
6. **Consistent API design** — Every endpoint uses the same response envelope pattern
7. **Fully typed** — Pydantic models on backend, TypeScript interfaces on frontend — no `any` types

---

## Slide 22 — Q&A

### Thank You!

**Engineering Delivery Health Analyzer**
*Real-time delivery risk and workload visibility*

- 📂 Repository: `EngineeringDeliveryHealthAnalyzer/`
- 🖥️ Frontend: `http://localhost:5173`
- ⚙️ Backend API: `http://localhost:8000/docs`
- 📊 Interactive API Docs: Swagger UI at `/docs`
