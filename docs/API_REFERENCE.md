# Engineering Delivery Health Analyzer — API Reference

**Base URL:** `http://localhost:8000`  
**Interactive Docs:** `http://localhost:8000/docs`  
**OpenAPI Spec:** `docs/openapi.json`

All responses use a consistent envelope:
```json
{
  "data": <payload>,
  "meta": { "generated_at": "2026-03-15T07:50:15.703044+00:00" }
}
```

---

## Dashboard Endpoints

### GET `/api/v1/issues`
Returns issues from the loaded dataset. Supports optional filters.

**Query params:**

| Param | Required | Description |
|---|---|---|
| `space` | ❌ | Filter by space: `TSA-SITE` \| `Voice Policy Engine 2.0` \| `RCEM 3.0` \| `AIP Risk Support` |
| `fix_version` | ❌ | Filter by exact fix version name (see table below for examples per space) |
| `status` | ❌ | Filter by status: `Open` \| `In Progress` \| `Blocked` \| `Done` |
| `assignee` | ❌ | Filter by assignee display name (case-insensitive) |

**Sample fix versions per space:**

| Space | Example fix versions |
|---|---|
| `TSA-SITE` | `SITE 14.1` · `SITE 14.1 GR` · `SITE 14.1 TMO` · `SITE 15.0` |
| `Voice Policy Engine 2.0` | `VPE2.0.22.6.0` · `VPE2-2.0-R221001` · `VPE2-2.0-R220901` |
| `RCEM 3.0` | `RCEM 3.0` · `RNS-Prior-Apr-2022-Releases` · `Unassigned` |
| `AIP Risk Support` | `AIPRS` · `None` |

> Use `GET /api/v1/jira/fix-versions?project=TSITE` (or `VPE2`, `RCEM3`, `RCEM32`) to get the live version list from JIRA.

**Response `data`:** Array of `Issue` objects.

```json
[
  {
    "issue_id": "TSITE-12413",
    "title": "TMO TACC R1/2026: user settings mangled",
    "status": "In Progress",
    "priority": "Medium",
    "days_open": 9,
    "assignee": "Sukrutha Karthik",
    "fix_version": "SITE 14.1 TMO",
    "fix_version_released": false,
    "fix_version_date": "",
    "space": "TSA-SITE",
    "type": "Bug"
  }
]
```

**Field reference:**

| Field | Type | Values |
|---|---|---|
| `issue_id` | string | JIRA key, e.g. `TSITE-12413` |
| `title` | string | Issue summary |
| `project` | string | JIRA project key, e.g. `TSITE`, `VPE2`, `RCEM3`, `RCEM32` |
| `status` | string | `Open` \| `In Progress` \| `Blocked` \| `Done` |
| `priority` | string | `Low` \| `Medium` \| `High` \| `Critical` |
| `days_open` | integer | Calendar days since created |
| `assignee` | string | Display name |
| `fix_version` | string | Fix version or `"Unassigned"` (e.g. `SITE 14.1 GR`, `SITE 14.1 TMO`) |
| `fix_version_released` | boolean | `true` when the fix version is formally released in JIRA |
| `fix_version_date` | string | ISO date of the release, e.g. `"2025-11-14"`; empty string if unset |
| `space` | string | Product area, e.g. `"TSA-SITE"`, `"Voice Policy Engine 2.0"`, `"RCEM 3.0"`, `"AIP Risk Support"` |
| `type` | string | `Bug` \| `Feature` \| `Task` \| `Improvement` |

---

### GET `/api/v1/health-score`
Returns the team-level RAG health score plus per-issue scored details. Filter by space and/or fix version to scope the score to a single release or product area.

**Query params:**

| Param | Required | Description |
|---|---|---|
| `space` | ❌ | Filter by space: `TSA-SITE` \| `Voice Policy Engine 2.0` \| `RCEM 3.0` \| `AIP Risk Support` |
| `fix_version` | ❌ | Filter by exact fix version, e.g. `SITE 14.1`, `SITE 14.1 GR`, `VPE2.0.22.6.0` |

**Examples:**
```
# All issues (whole dataset)
GET /api/v1/health-score

# Scoped to a single space
GET /api/v1/health-score?space=TSA-SITE

# Scoped to a specific release
GET /api/v1/health-score?space=TSA-SITE&fix_version=SITE+14.1
GET /api/v1/health-score?space=TSA-SITE&fix_version=SITE+14.1+GR
GET /api/v1/health-score?space=Voice+Policy+Engine+2.0&fix_version=VPE2.0.22.6.0
GET /api/v1/health-score?space=RCEM+3.0
```

**Response `data`:** `HealthSummary` object.

```json
{
  "team_score": 55,
  "rag": "Amber",
  "total_issues": 74,
  "issues": [
    {
      "issue_id": "TSITE-12413",
      "title": "...",
      "status": "In Progress",
      "priority": "Medium",
      "days_open": 9,
      "assignee": "Sukrutha Karthik",
      "fix_version": "SITE 14.1",
      "fix_version_released": true,
      "space": "TSA-SITE",
      "type": "Bug",
      "health_score": 63,
      "rag": "Amber",
      "bottleneck": false,
      "bottleneck_reason": null
    }
  ]
}
```

**Scoring formula (0–100):**
```
score = 0.4 × status_score + 0.3 × priority_score + 0.3 × age_score
age_score = max(0, 100 - days_open × decay_rate)
```
Decay rate by type: Bug=7.0 · Task=3.0 · Improvement=2.0 · Feature=1.0

| Status | Score | Priority | Score |
|---|---|---|---|
| Done | 100 | Low | 100 |
| In Progress | 70 | Medium | 75 |
| Open | 50 | High | 40 |
| Blocked | 0 | Critical | 10 |

**RAG thresholds:**
- 🟢 **Green** — score ≥ 75
- 🟡 **Amber** — score 50–74
- 🔴 **Red** — score < 50

**`team_score`** = average score of all non-Done issues (100 if none active).

---

### GET `/api/v1/bottlenecks`
Returns issues flagged as bottlenecks, sorted by risk (Blocked first, then by `days_open` descending). Filter by space and/or fix version to scope to a release.

**Query params:**

| Param | Required | Description |
|---|---|---|
| `space` | ❌ | Filter by space: `TSA-SITE` \| `Voice Policy Engine 2.0` \| `RCEM 3.0` \| `AIP Risk Support` |
| `fix_version` | ❌ | Filter by exact fix version, e.g. `SITE 14.1 GR`, `SITE 14.1 TMO` |

**Examples:**
```
# All bottlenecks across the loaded dataset
GET /api/v1/bottlenecks

# Bottlenecks in a specific release
GET /api/v1/bottlenecks?space=TSA-SITE&fix_version=SITE+14.1
GET /api/v1/bottlenecks?space=TSA-SITE&fix_version=SITE+14.1+GR
GET /api/v1/bottlenecks?space=Voice+Policy+Engine+2.0&fix_version=VPE2.0.22.6.0
GET /api/v1/bottlenecks?space=RCEM+3.0
```

**Response `data`:** Array of `IssueWithScore` (same shape as items in `/health-score`).

**Bottleneck rules by type (any one triggers it):**

| Type | Blocked | Critical | In Progress stale | Open stale |
|---|---|---|---|---|
| Bug | always | > 5 days | > 7 days | > 5 days |
| Feature | always | > 5 days | > 21 days | > 30 days |
| Task / Improvement | always | > 5 days | > 14 days | > 21 days |

---

### GET `/api/v1/health-score/by-release`
Returns health score aggregated per fix version, grouped by `(space, fix_version)` to prevent cross-space collisions. Sorted by `fix_version_date` descending (most recent first).

**Query params:**

| Param | Required | Default | Description |
|---|---|---|---|
| `space` | ❌ | all | Filter by space name. Omit to see all spaces in one response. |
| `limit` | ❌ | `5` | Max fix versions to return (1–50) |

**Examples:**
```
# All spaces (multi-space dataset)
GET /api/v1/health-score/by-release?limit=10

# TSA-SITE only
GET /api/v1/health-score/by-release?space=TSA-SITE

# Voice Policy Engine 2.0
GET /api/v1/health-score/by-release?space=Voice+Policy+Engine+2.0

# RCEM 3.0
GET /api/v1/health-score/by-release?space=RCEM+3.0

# AIP Risk Support
GET /api/v1/health-score/by-release?space=AIP+Risk+Support
```

**Response `data`:** Array of `ReleaseHealth` objects.

```json
[
  {
    "fix_version": "SITE 14.1",
    "fix_version_date": "2025-11-14",
    "released": true,
    "space": "TSA-SITE",
    "score": 55,
    "rag": "Amber",
    "total_issues": 74,
    "open_issues": 2,
    "in_progress_issues": 0,
    "blocked_issues": 0,
    "done_issues": 72,
    "bottleneck_count": 28
  },
  {
    "fix_version": "VPE2.0.22.6.0",
    "fix_version_date": "",
    "released": true,
    "space": "Voice Policy Engine 2.0",
    "score": 72,
    "rag": "Amber",
    "total_issues": 30,
    "open_issues": 5,
    "in_progress_issues": 8,
    "blocked_issues": 1,
    "done_issues": 16,
    "bottleneck_count": 4
  }
]
```

| Field | Description |
|---|---|
| `fix_version` | Release label (e.g. `SITE 14.1`, `SITE 14.1 GR`) |
| `fix_version_date` | ISO date of the release, e.g. `"2025-11-14"`; empty if unset |
| `released` | `true` when formally released in JIRA |
| `space` | Product area, e.g. `"TSA-SITE"` |
| `score` | Average health score of non-Done issues (100 if all Done) |
| `rag` | RAG classification of the release |
| `total_issues` | All issues in this release |
| `open_issues` | Count with status `Open` |
| `in_progress_issues` | Count with status `In Progress` |
| `blocked_issues` | Count with status `Blocked` |
| `done_issues` | Count with status `Done` |
| `bottleneck_count` | Issues flagged as bottlenecks |

---

### GET `/api/v1/health-score/summary`
Lightweight summary: RAG counts + team score per space, without the full issue list.
Designed for landing page cards where individual issues are not needed.

**Parameters:**

| Param | Type | Required | Description |
|---|---|---|---|
| `project` | `string` | No | JIRA project ID, e.g. `TSITE`, `VPE2`, `RCEM3` |
| `fix_version` | `string` | No | Exact fix version name, e.g. `SITE 15.0` |

**Examples:**
```
GET /api/v1/health-score/summary?project=TSITE
GET /api/v1/health-score/summary?project=TSITE&fix_version=SITE+15.0
```

**Response `data`:**
```json
{
  "space": "TSA-SITE",
  "team_score": 68,
  "rag": "Amber",
  "total_issues": 100,
  "red": 5,
  "amber": 72,
  "green": 23
}
```

| Field | Description |
|---|---|
| `space` | Product area, e.g. `"TSA-SITE"` |
| `team_score` | Average health score of non-Done issues (100 if all Done) |
| `rag` | RAG classification of the team score |
| `total_issues` | Total issues matching filters |
| `red` | Count of issues with Red RAG status |
| `amber` | Count of issues with Amber RAG status |
| `green` | Count of issues with Green RAG status |

---

### GET `/api/v1/workload`
Returns active issue counts grouped by priority (excludes `Done` issues).

**Response `data`:**
```json
{
  "Critical": 0,
  "High": 1,
  "Medium": 6,
  "Low": 0
}
```

---

## JIRA Sync Endpoints

> These are for backend/admin use. The frontend can call `/api/v1/jira/sync` to provide a "Refresh Data" button.

### GET `/api/v1/jira/spaces`
Returns all known spaces and their mapped JIRA project keys. Use this to populate a Space dropdown in the UI.

**Response `data`:**
```json
[
  { "space": "TSA-SITE",               "projects": ["TSITE"] },
  { "space": "Voice Policy Engine 2.0", "projects": ["VPE2"] },
  { "space": "RCEM 3.0",               "projects": ["RCEM3"] },
  { "space": "AIP Risk Support",      "projects": ["SIPRS"] }
]
```

---

### GET `/api/v1/jira/projects`
Returns all JIRA projects visible to the configured credentials.

**Response `data`:** Array of project objects.
```json
[
  { "key": "TSITE", "name": "TSA SITE" },
  { "key": "VPE2",  "name": "Voice Policy Engine 2.0" }
]
```

---

### GET `/api/v1/jira/active-release?project={key}`
Returns the current active (unreleased, non-archived) release for a project. The active release is the unreleased version whose release date is closest to today.

**Query params:**

| Param | Required | Description |
|---|---|---|
| `project` | ✅ | JIRA project key, e.g. `TSITE`, `VPE2`, `RCEM3`, `RCEM32` |

**Response `data`:** Single version object, or **404** if no unreleased version exists.
```json
{
  "id": "48536",
  "name": "SITE 14.1 GR",
  "released": "False",
  "archived": "False",
  "releaseDate": "2026-03-13"
}
```

---

### GET `/api/v1/jira/users?project={key}`
Returns assignable users for a JIRA project.

**Query params:**

| Param | Required | Description |
|---|---|---|
| `project` | ✅ | JIRA project key, e.g. `TSITE` |

**Response `data`:** Array of user objects.
```json
[
  {
    "account_id": "712020:...",
    "display_name": "John Doe",
    "email": "user@yourcompany.com"
  }
]
```

---

### GET `/api/v1/jira/sync`
Fetches issues from JIRA and refreshes the backend dataset. All dashboard endpoints immediately return the new data after this call.

Provide **either** `space` (preferred) or `project`. `space` automatically resolves to the correct project key(s).

**Query params:**

| Param | Required | Default | Description |
|---|---|---|---|
| `space` | ✅ (or `project`) | — | Space name, e.g. `TSA-SITE`. Resolves to project key(s) automatically. |
| `project` | ✅ (or `space`) | — | JIRA project key, e.g. `TSITE`. Used when `space` is not provided. |
| `fix_version` | ❌ | all | Fix version prefix, e.g. `SITE 14.1` matches `SITE 14.1`, `SITE 14.1 GR`, `SITE 14.1 TMO` |
| `assignee` | ❌ | all | Filter by assignee display name |
| `max_results` | ❌ | `200` | Max issues to fetch (1–1000) |

**Examples:**
```
# All SITE 14.1 issues by space (preferred)
GET /api/v1/jira/sync?space=TSA-SITE&fix_version=SITE+14.1

# Voice Policy Engine 2.0 issues
GET /api/v1/jira/sync?space=Voice+Policy+Engine+2.0

# RCEM 3.0 issues
GET /api/v1/jira/sync?space=RCEM+3.0

# Fallback: by project key
GET /api/v1/jira/sync?project=TSITE&assignee=Sukrutha%20Karthik
```

**Response `data`:**
```json
{
  "synced": 100,
  "space": "TSA-SITE",
  "project": null,
  "assignee": null,
  "fix_version_prefix": "SITE 14.1",
  "file": "...\\data\\issues.json"
}
```

---

## Error Responses

| Status | Meaning |
|---|---|
| `400` | Bad request / missing required param |
| `404` | No issues found for given filters |
| `422` | Validation error (wrong param type) |
| `502` | JIRA API unreachable or auth failed |
