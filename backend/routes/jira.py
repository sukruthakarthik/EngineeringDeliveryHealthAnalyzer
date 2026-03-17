from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from analytics.jira_client import (
    fetch_fix_versions_for_project,
    fetch_issues,
    fetch_projects,
    fetch_users_for_project,
    get_spaces,
    resolve_projects_for_space,
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
    project: str = Query(..., description="JIRA project key: SITE | RCEM | VPE2"),
    limit: int = Query(5, ge=1, le=50, description="Number of most recent active fix versions to return (default 5)"),
) -> dict:
    """Return the most recent active fix versions for a JIRA project."""
    try:
        versions = fetch_fix_versions_for_project(project, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"JIRA API error: {exc}") from exc
    return make_response(versions)


@router.get("/users")
def list_users(project: str = Query(..., description="JIRA project key: SITE | RCEM | VPE2")) -> dict:
    """Return assignable users for a JIRA project."""
    try:
        users = fetch_users_for_project(project)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"JIRA API error: {exc}") from exc
    return make_response(users)


@router.get("/sync")
def sync_issues(
    project: str | None = Query(None, description="JIRA project key, e.g. TSITE, VPE2, RCEM3. Ignored when space is provided."),
    space: str | None = Query(None, description="Space name, e.g. 'TSA-SITE', 'Voice Policy Engine 2.0'. Resolves to project(s) automatically."),
    assignee: str | None = Query(None, description="Filter by assignee display name"),
    fix_version: str | None = Query(None, description="Fix version prefix, e.g. 'RCEM 2.3', 'SITE 14.1', 'VPE2 1.0'"),
    max_results: int = Query(200, ge=1, le=1000, description="Max issues to fetch"),
) -> dict:
    """
    Fetch issues from JIRA and write them to data/issues.json.
    Provide either *space* (preferred) or *project*. When *space* is given the
    project key is resolved automatically (one space may map to multiple projects).
    Clears the data_loader cache so subsequent API calls use fresh data.
    """
    if not space and not project:
        raise HTTPException(status_code=422, detail="Provide either 'space' or 'project' query parameter")

    if space:
        try:
            resolve_projects_for_space(space)  # validate early
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        issues = fetch_issues(
            project or "",
            assignee_name=assignee,
            fix_version_prefix=fix_version,
            max_results=max_results,
            space=space,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"JIRA API error: {exc}") from exc

    if not issues:
        raise HTTPException(status_code=404, detail="No issues found for the given filters")

    # Write to data/issues.json
    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)

    # Clear cached data so load_issues() picks up the new file
    from analytics.data_loader import load_issues
    load_issues.cache_clear()

    return make_response({
        "synced": len(issues),
        "space": space,
        "project": project,
        "assignee": assignee,
        "fix_version_prefix": fix_version,
        "file": str(_DATA_PATH),
    })
