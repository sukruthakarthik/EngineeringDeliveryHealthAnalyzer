from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load .env from backend directory
_ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(_ENV_PATH)

JIRA_URL: str = os.environ["JIRA_URL"].rstrip("/")
JIRA_EMAIL: str = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN: str = os.environ["JIRA_API_TOKEN"]

_AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
_HEADERS = {"Accept": "application/json"}
_API_BASE = f"{JIRA_URL}/rest/api/3"

# ── Status / Priority mapping from JIRA → our model ──────────────────────

_STATUS_MAP: dict[str, str] = {
    # TSITE-specific statuses
    "open": "Open",
    "estimation request": "Open",
    "in planning": "Open",
    "in development": "In Progress",
    "in progress": "In Progress",
    "in review": "In Progress",
    "in testing": "In Progress",
    "l3 analysis": "In Progress",
    "information provided": "Blocked",
    "blocked": "Blocked",
    "on hold": "Blocked",
    "fixed": "Done",
    "closed": "Done",
    "resolved": "Done",
    "released": "Done",
    "rejected": "Done",
    "rejected by dev": "Done",
    "withdrawn": "Done",
    "done": "Done",
    "complete": "Done",
    "completed": "Done",
    # Generic fallbacks
    "to do": "Open",
    "new": "Open",
    "backlog": "Open",
    "reopened": "Open",
    "code review": "In Progress",
    "review": "In Progress",
    "impediment": "Blocked",
    # AIPRS-specific statuses
    "information requested (o)": "In Progress",
    "information provided": "In Progress",
    "information not provided": "Done",
    "duplicate": "Done",
}

_PRIORITY_MAP: dict[str, str] = {
    # Mobileum JIRA uses numbered priorities
    "1-blocker": "Critical",
    "2-high": "High",
    "3-medium": "Medium",
    "5-very low": "Low",
    # Generic fallbacks
    "highest": "Critical",
    "critical": "Critical",
    "blocker": "Critical",
    "high": "High",
    "medium": "Medium",
    "normal": "Medium",
    "low": "Low",
    "lowest": "Low",
    "trivial": "Low",
    "4-low": "Low",
}

# ── Space ↔ Project mapping ───────────────────────────────────────────────

_SPACE_TO_PROJECTS: dict[str, list[str]] = {
    "TSA-SITE": ["TSITE"],
    "RCEM 3.0": ["RCEM3"],
    "Voice Policy Engine 2.0": ["VPE2"],
    "AIP Risk Support": ["AIPRS"],
    "Steering 9.0": ["NTR9"],
}

_PROJECT_TO_SPACE: dict[str, str] = {
    proj: space
    for space, projects in _SPACE_TO_PROJECTS.items()
    for proj in projects
}


def get_spaces() -> dict[str, list[str]]:
    """Return all known spaces as a dict mapping space name → project keys."""
    return {space: projects for space, projects in _SPACE_TO_PROJECTS.items()}


def resolve_projects_for_space(space: str) -> list[str]:
    """Resolve a space name to its JIRA project key(s). Raises ValueError if unknown."""
    projects = _SPACE_TO_PROJECTS.get(space)
    if not projects:
        known = ", ".join(sorted(_SPACE_TO_PROJECTS))
        raise ValueError(f"Unknown space '{space}'. Known spaces: {known}")
    return projects


_TYPE_MAP: dict[str, str] = {
    # TSITE-specific types
    "general testing defect": "Bug",
    "external defect": "Bug",
    "qe defect": "Bug",
    "story": "Feature",
    "epic": "Feature",
    "task": "Task",
    "sub-task": "Task",
    "subtask": "Task",
    "sw release": "Task",
    "sw-update": "Task",
    "tracking item": "Task",
    "information request": "Task",
    "documentation_global": "Improvement",
    "improvement": "Improvement",
    "enhancement": "Improvement",
    # Generic fallbacks
    "bug": "Bug",
    "feature": "Feature",
    "new feature": "Feature",
}


def _map_status(raw: str) -> str:
    return _STATUS_MAP.get(raw.lower().strip(), "Open")


def _map_priority(raw: str) -> str:
    return _PRIORITY_MAP.get(raw.lower().strip(), "Medium")


def _map_type(raw: str) -> str:
    return _TYPE_MAP.get(raw.lower().strip(), "Task")


def _days_since(created_str: str) -> int:
    """Calculate days open from JIRA created timestamp."""
    created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
    delta = datetime.now(timezone.utc) - created
    return max(0, delta.days)


def _extract_fix_version(fields: dict) -> tuple[str, bool, str]:
    """
    Extract fix version name, released status, and release date from JIRA fixVersions field.
    Returns (name, released, releaseDate) — releaseDate is ISO date string or "" if unset.
    """
    fix_versions: list[dict] = fields.get("fixVersions") or []
    if fix_versions:
        active = [v for v in fix_versions if not v.get("archived", False)]
        candidates = active if active else fix_versions
        chosen = candidates[-1]
        return (
            chosen.get("name", "Unassigned"),
            bool(chosen.get("released", False)),
            chosen.get("releaseDate", ""),
        )
    return "Unassigned", False, ""


# ── Public API ────────────────────────────────────────────────────────────


def fetch_projects() -> list[dict[str, str]]:
    """Return list of JIRA projects visible to the authenticated user."""
    resp = requests.get(
        f"{_API_BASE}/project/search",
        auth=_AUTH,
        headers=_HEADERS,
        params={"maxResults": 100, "orderBy": "name"},
        timeout=30,
    )
    resp.raise_for_status()
    projects = resp.json().get("values", [])
    return [
        {"key": p["key"], "name": p["name"]}
        for p in projects
    ]


def fetch_fix_versions_for_project(project_key: str, limit: int = 0) -> list[dict[str, str]]:
    """Return current, past, and the single next active release for a project.

    Versions are sorted by release date descending (most recent first).
    The one nearest future-dated unreleased version is always included so the
    currently-in-progress release is visible. All other future versions are excluded.

    Args:
        project_key: JIRA project key, e.g. "TSITE", "RCEM", "VPE2".
        limit: When > 0, return only the `limit` most recent eligible versions
               (the active upcoming release counts toward the limit).
               Pass 0 for all eligible versions.
    """
    from datetime import date as _date

    resp = requests.get(
        f"{_API_BASE}/project/{project_key}/versions",
        auth=_AUTH,
        headers=_HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    versions = resp.json()

    today = _date.today().isoformat()  # e.g. "2026-03-18"

    past_or_current: list[dict] = []
    upcoming: list[dict] = []

    for v in versions:
        if v.get("archived", False):
            continue
        entry = {
            "id": v["id"],
            "name": v["name"],
            "released": str(v.get("released", False)),
            "archived": str(v.get("archived", False)),
            "releaseDate": v.get("releaseDate", ""),
        }
        release_date = v.get("releaseDate", "")
        if not release_date or release_date <= today:
            past_or_current.append(entry)
        else:
            upcoming.append(entry)

    # Sort past/current newest-first
    past_or_current.sort(key=lambda v: v.get("releaseDate") or "0", reverse=True)

    # Include only the single nearest upcoming release (smallest future date)
    upcoming.sort(key=lambda v: v.get("releaseDate") or "9")
    next_release = [upcoming[0]] if upcoming else []

    # Active release first, then past releases
    eligible = next_release + past_or_current

    if limit > 0:
        return eligible[:limit]
    return eligible


def fetch_active_release(project_key: str) -> dict[str, str] | None:
    """Return the current active (unreleased, non-archived) release for a project.

    The active release is the unreleased version whose release date is closest
    to today — whether the date is slightly in the past (overdue) or in the
    future.  If no unreleased versions have a release date, the first
    unreleased version (alphabetically) is returned as a fallback.

    Returns a dict with keys ``id``, ``name``, ``released``, ``archived``,
    ``releaseDate``, or ``None`` if every version is already released/archived.
    """
    from datetime import date as _date

    resp = requests.get(
        f"{_API_BASE}/project/{project_key}/versions",
        auth=_AUTH,
        headers=_HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    versions: list[dict] = resp.json()
    today = _date.today().isoformat()

    unreleased: list[dict] = []
    for v in versions:
        if v.get("archived", False) or v.get("released", False):
            continue
        unreleased.append({
            "id": v["id"],
            "name": v["name"],
            "released": str(v.get("released", False)),
            "archived": str(v.get("archived", False)),
            "releaseDate": v.get("releaseDate", ""),
        })

    if not unreleased:
        return None

    # Pick the version whose releaseDate is closest to today
    dated = [v for v in unreleased if v["releaseDate"]]
    if dated:
        dated.sort(key=lambda v: abs(
            (_date.fromisoformat(v["releaseDate"]) - _date.fromisoformat(today)).days
        ))
        return dated[0]

    # Fallback: no dates at all — return first alphabetically
    unreleased.sort(key=lambda v: v["name"])
    return unreleased[0]


def fetch_users_for_project(project_key: str) -> list[dict[str, str]]:
    """Return assignable users for a given JIRA project."""
    resp = requests.get(
        f"{_API_BASE}/user/assignable/search",
        auth=_AUTH,
        headers=_HEADERS,
        params={"project": project_key, "maxResults": 200},
        timeout=30,
    )
    resp.raise_for_status()
    users = resp.json()
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for u in users:
        display = u.get("displayName", "Unknown")
        account_id = u.get("accountId", "")
        if account_id and account_id not in seen:
            seen.add(account_id)
            result.append({
                "account_id": account_id,
                "display_name": display,
                "email": u.get("emailAddress", ""),
            })
    result.sort(key=lambda x: x["display_name"])
    return result


def fetch_issues(
    project_key: str,
    assignee_name: str | None = None,
    fix_version_prefix: str | None = None,
    max_results: int = 200,
    *,
    space: str | None = None,
) -> list[dict]:
    """
    Fetch issues from JIRA for a project, optionally filtered by assignee
    and/or fix version prefix (e.g. "SITE 14.1" matches "SITE 14.1",
    "SITE 14.1 GR", "SITE 14.1 TMO", etc.).

    If *space* is provided, it overrides *project_key* by resolving the space
    to one or more projects and fetching issues from all of them.
    """
    if space:
        project_keys = resolve_projects_for_space(space)
        all_results: list[dict] = []
        per_project = max(1, max_results // len(project_keys))
        for pk in project_keys:
            all_results.extend(
                fetch_issues(
                    pk,
                    assignee_name=assignee_name,
                    fix_version_prefix=fix_version_prefix,
                    max_results=per_project,
                )
            )
        return all_results[:max_results]
    jql_parts = [f'project = "{project_key}"']
    if assignee_name:
        safe_name = assignee_name.replace('"', '\\"')
        jql_parts.append(f'assignee = "{safe_name}"')
    if fix_version_prefix:
        # Resolve all matching version names from the project, then use
        # fixVersion in (...) for precise JQL — avoids text-search quirks.
        all_versions = fetch_fix_versions_for_project(project_key)
        matching = [
            v["name"] for v in all_versions
            if v["name"].lower().startswith(fix_version_prefix.lower())
        ]
        if not matching:
            return []  # No versions match — return empty rather than all issues
        escaped = ", ".join(f'"{v}"' for v in matching)
        jql_parts.append(f"fixVersion in ({escaped})")
    jql = " AND ".join(jql_parts) + " ORDER BY created DESC"

    all_issues: list[dict] = []
    start_at = 0
    fields = "summary,status,priority,assignee,issuetype,created,fixVersions"

    while start_at < max_results:
        batch_size = min(100, max_results - start_at)
        resp = requests.get(
            f"{_API_BASE}/search/jql",
            auth=_AUTH,
            headers=_HEADERS,
            params={
                "jql": jql,
                "fields": fields,
                "maxResults": batch_size,
                "startAt": start_at,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("issues", [])
        if not batch:
            break

        for raw in batch:
            f = raw["fields"]
            assignee_field = f.get("assignee") or {}
            _fv_name, _fv_released, _fv_date = _extract_fix_version(f)
            issue = {
                "issue_id": raw["key"],
                "title": f.get("summary", "Untitled"),
                "project": project_key,
                "status": _map_status(
                    (f.get("status") or {}).get("name", "Open")
                ),
                "priority": _map_priority(
                    (f.get("priority") or {}).get("name", "Medium")
                ),
                "days_open": _days_since(f.get("created", "2026-01-01T00:00:00+00:00")),
                "assignee": assignee_field.get("displayName", "Unassigned"),
                "fix_version": _fv_name,
                "fix_version_released": _fv_released,
                "fix_version_date": _fv_date,
                "space": _PROJECT_TO_SPACE.get(project_key, project_key),
                "type": _map_type(
                    (f.get("issuetype") or {}).get("name", "Task")
                ),
            }
            all_issues.append(issue)

        start_at += len(batch)
        if start_at >= data.get("total", 0):
            break

    return all_issues
