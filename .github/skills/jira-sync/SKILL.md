---
name: jira-sync
description: "Add, modify, or debug JIRA field mappings and sync logic for the Engineering Delivery Health Analyzer. USE FOR: adding new status/priority/type mappings; changing assignee or project filters; debugging JIRA API errors; extending the sync endpoint; updating the data pipeline from JIRA to issues.json. DO NOT USE FOR: frontend components; health scoring formula changes; general FastAPI questions."
argument-hint: "Describe the mapping change or sync issue, e.g. 'add new status Pending Review'"
---

# JIRA Sync Skill

## Key Files

| File | Purpose |
|---|---|
| `backend/analytics/jira_client.py` | All JIRA API calls + field mappings |
| `backend/routes/jira.py` | Sync/projects/users endpoints |
| `backend/.env` | Credentials (never commit) |
| `data/issues.json` | Output — the backend cache |

## Mobileum JIRA Instance Facts

**Base URL:** `https://mobileumjira.atlassian.net`  
**API version:** REST API v3 — `{base}/rest/api/3/`  
**Auth:** HTTP Basic Auth — email + API token

### Critical API Quirk
The old `/rest/api/3/search` endpoint returns **410 Gone** on this instance.  
Always use:
```
GET /rest/api/3/search/jql?jql=...&fields=...&maxResults=N&startAt=N
```

### Actual Priority Values (not standard JIRA)
Mobileum uses **numbered** priorities — map by exact lowercase match:

| JIRA value | Our model |
|---|---|
| `1-Blocker` | `Critical` |
| `2-High` | `High` |
| `3-Medium` | `Medium` |
| `5-Very Low` | `Low` |

### Actual Status Values (TSITE project)
Custom workflow — not standard JIRA statuses:

| JIRA value | Our model |
|---|---|
| `Open`, `Estimation Request`, `In Planning` | `Open` |
| `In Development`, `In Progress`, `In Review`, `In Testing`, `L3 Analysis` | `In Progress` |
| `Information Provided`, `On Hold` | `Blocked` |
| `Fixed`, `Closed`, `Resolved`, `Released`, `Rejected`, `Rejected by Dev`, `Withdrawn`, `Done` | `Done` |

### Actual Issue Type Values (TSITE project)

| JIRA value | Our model | Notes |
|---|---|---|
| `General Testing Defect` | `Bug` | Defect found during general testing |
| `External Defect` | `Bug` | Defect reported from outside the team |
| `QE Defect` | `Bug` | Defect opened against a Story currently in the testing cycle — created by QE on an in-progress Story; highest urgency |
| `Story` | `Feature` | |
| `Epic` | `Feature` | |
| `Task` | `Task` | |
| `Sub-task` | `Task` | |
| `SW Release` | `Task` | |
| `SW-Update` | `Task` | |
| `Tracking Item` | `Task` | |
| `Information Request` | `Task` | |
| `Documentation_Global` | `Improvement` | |
| `Documentation` | `Task` | |

## Procedure: Add a New Status Mapping

1. Read `backend/analytics/jira_client.py`
2. Find `_STATUS_MAP` dict
3. Add the new JIRA status (lowercase) → one of `Open | In Progress | Blocked | Done`
4. No restart needed — mapping is in-memory, takes effect on next sync call

## Procedure: Add a New Priority Mapping

1. Find `_PRIORITY_MAP` in `jira_client.py`
2. Add entry in `"n-name": "OurPriority"` format (lowercase key)
3. Valid target values: `Critical | High | Medium | Low`

## Procedure: Add a New Issue Type Mapping

1. Find `_TYPE_MAP` in `jira_client.py`
2. Add entry (lowercase JIRA type name → `Bug | Feature | Task | Improvement`)

## Space → Project Mapping

A **Space** is a logical grouping of JIRA project keys. The mapping is defined in `_SPACE_TO_PROJECTS` in `jira_client.py`:

| Space | JIRA Project Key |
|---|---|
| `TSA-SITE` | `TSITE` |
| `Voice Policy Engine 2.0` | `VPE2` |
| `RCEM 3.0` | `RCEM3` |
| `RCEM 3.2` | `RCEM32` |

`_PROJECT_TO_SPACE` is the reverse lookup, auto-generated from the same dict. Every synced issue gets a `space` field populated from this map.

To add a new space:
1. Add an entry to `_SPACE_TO_PROJECTS` in `jira_client.py`.
2. No other code changes needed — `_PROJECT_TO_SPACE` rebuilds automatically.

## Procedure: Change Sync Filters

The sync endpoint in `backend/routes/jira.py` accepts:
- `space` (preferred) — resolves to one or more project keys automatically, e.g. `TSA-SITE`
- `project` (fallback) — JIRA project key, e.g. `TSITE`. Used when `space` is not provided.
- `fix_version` (optional) — fix version prefix, e.g. `SITE 14.1`
- `assignee` (optional) — exact display name, e.g. `Sukrutha Karthik`
- `max_results` (optional, default 200, max 1000)

To add a new filter (e.g. issue type):
1. Add a `Query(...)` param to `sync_issues()` in `routes/jira.py`
2. Pass it into `fetch_issues()` in `jira_client.py`
3. Add it to the JQL in `fetch_issues()`:
   ```python
   jql_parts.append(f'issuetype = "{issue_type}"')
   ```

## Procedure: Debug a JIRA API Error

| HTTP status | Likely cause | Fix |
|---|---|---|
| `401` | Wrong API token or email in `.env` | Regenerate token at `id.atlassian.net/manage-profile/security/api-tokens` |
| `400` | Bad JQL — special chars in assignee name | Escape quotes: `name.replace('"', '\\"')` |
| `404` | Wrong project key | Call `GET /api/v1/jira/projects` to list valid keys |
| `410` | Using deprecated `/search` endpoint | Use `/search/jql` instead |
| `502` | Network / JIRA down | Check connectivity; error message is forwarded in response |

## Cache-Clear Pattern (IMPORTANT)

After writing a new `issues.json`, always clear the LRU cache or the dashboard endpoints will keep returning stale data:

```python
from analytics.data_loader import load_issues
load_issues.cache_clear()
```

This is already done in `routes/jira.py` `sync_issues()`. If you add another write path, replicate this pattern.

## Fix Versions

All Mobileum projects use **Fix Versions** (e.g. `SITE 15.0`, `INTERNAL`). The `_extract_fix_version()` function reads the `fixVersions` field:

- Picks the last non-archived version
- Falls back to any version if all are archived
- Returns `"Unassigned"` when the field is empty

**Fields fetched per issue:**
```
summary, status, priority, assignee, issuetype, created, fixVersions
```
