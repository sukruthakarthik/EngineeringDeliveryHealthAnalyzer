from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from analytics.jira_client import (
    fetch_active_release,
    fetch_fix_versions_for_project,
    fetch_issues,
    fetch_projects,
    fetch_users_for_project,
    get_spaces,
)
from models.response import make_response

router = APIRouter(prefix="/api/v1/jira", tags=["jira"])

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "issues.json"


@router.get("/spaces")
def list_spaces() -> dict:
    """Return all known spaces and their mapped JIRA project keys."""
    return make_response(get_spaces())


@router.get("/projects")
def list_projects() -> dict:
    """Return all JIRA projects visible to the authenticated user."""
    try:
        projects = fetch_projects()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"JIRA API error: {exc}") from exc
    return make_response(projects)


@router.get("/fix-versions")
def list_fix_versions(
    project: str = Query(..., description="JIRA project key: TSITE | RCEM | VPE2"),
    limit: int = Query(10, ge=1, le=100, description="Max fix versions to return, most recent first (default 10)"),
) -> dict:
    """Return the most recent non-archived fix versions for a JIRA project, sorted by release date descending."""
    try:
        versions = fetch_fix_versions_for_project(project, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"JIRA API error: {exc}") from exc
    return make_response(versions)


@router.get("/active-release")
def get_active_release(
    project: str = Query(..., description="JIRA project key: TSITE | RCEM3 | VPE2 | RCEM32"),
) -> dict:
    """Return the current active (unreleased) release for a project."""
    try:
        release = fetch_active_release(project)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"JIRA API error: {exc}") from exc
    if release is None:
        raise HTTPException(status_code=404, detail="No active (unreleased) release found")
    return make_response(release)


@router.get("/users")
def list_users(project: str = Query(..., description="JIRA project key: TSITE | RCEM | VPE2")) -> dict:
    """Return assignable users for a JIRA project."""
    try:
        users = fetch_users_for_project(project)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"JIRA API error: {exc}") from exc
    return make_response(users)


@router.get("/sync")
def sync_issues(
    project: str = Query(..., description="JIRA project ID, e.g. TSITE, VPE2, RCEM3, RCEM32"),
    assignee: str | None = Query(None, description="Filter by assignee display name"),
    fix_version: str | None = Query(None, description="Fix version prefix, e.g. 'RCEM 2.3', 'SITE 14.1', 'VPE2 1.0'"),
    max_results: int = Query(200, ge=1, le=1000, description="Max issues to fetch"),
) -> dict:
    """
    Fetch issues from JIRA and write them to data/issues.json.
    Provide *project* as a JIRA project ID (e.g. TSITE, VPE2, RCEM3).
    Clears the data_loader cache so subsequent API calls use fresh data.
    """
    try:
        issues = fetch_issues(
            project,
            assignee_name=assignee,
            fix_version_prefix=fix_version,
            max_results=max_results,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"JIRA API error: {exc}") from exc

    if not issues:
        raise HTTPException(status_code=404, detail="No issues found for the given filters")

    # Merge into data/issues.json — replace only issues belonging to this project,
    # leaving issues from other projects untouched.
    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict] = []
    if _DATA_PATH.exists():
        try:
            with _DATA_PATH.open("r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing = []

    # When a fix_version filter is used, only replace issues matching that
    # prefix — keep the project's other fix-version issues intact.
    # Without a filter, replace ALL issues for the project.
    synced_ids = {i["issue_id"] for i in issues}
    if fix_version:
        prefix = fix_version.lower()
        kept = [
            i for i in existing
            if i.get("project") != project
            or (
                not (i.get("fix_version", "").lower().startswith(prefix))
                and i.get("issue_id") not in synced_ids
            )
        ]
    else:
        kept = [i for i in existing if i.get("project") != project]
    merged = kept + issues

    with _DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    # Clear cached data so load_issues() picks up the new file
    from analytics.data_loader import load_issues
    load_issues.cache_clear()

    return make_response({
        "synced": len(issues),
        "total_in_file": len(merged),
        "project": project,
        "assignee": assignee,
        "fix_version_prefix": fix_version,
        "file": str(_DATA_PATH),
    })
