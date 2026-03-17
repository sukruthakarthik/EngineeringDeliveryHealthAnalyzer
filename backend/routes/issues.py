from fastapi import APIRouter, Query

from analytics.data_loader import load_issues
from models.response import make_response

router = APIRouter(prefix="/api/v1", tags=["issues"])


@router.get("/issues")
def get_issues(
    space: str | None = Query(
        None,
        description="Filter by space name, e.g. 'TSA-SITE', 'Voice Policy Engine 2.0', 'RCEM 3.0', 'RCEM 3.2'",
    ),
    fix_version: str | None = Query(
        None,
        description=(
            "Filter by exact fix version name. "
            "TSA-SITE examples: 'SITE 14.1', 'SITE 14.1 GR', 'SITE 14.1 TMO'. "
            "VPE2 examples: 'VPE2.0.22.6.0', 'VPE2-2.0-R221001'. "
            "RCEM examples: 'RCEM 3.0', 'Unassigned'."
        ),
    ),
    status: str | None = Query(
        None,
        description="Filter by status: 'Open' | 'In Progress' | 'Blocked' | 'Done'",
    ),
    assignee: str | None = Query(None, description="Filter by assignee display name"),
) -> dict:
    issues = load_issues()
    if space:
        issues = [i for i in issues if i.space == space]
    if fix_version:
        issues = [i for i in issues if i.fix_version == fix_version]
    if status:
        issues = [i for i in issues if i.status == status]
    if assignee:
        issues = [i for i in issues if i.assignee.lower() == assignee.lower()]
    return make_response([i.model_dump() for i in issues])
