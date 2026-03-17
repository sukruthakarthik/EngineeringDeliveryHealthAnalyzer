from fastapi import APIRouter, Query

from analytics.data_loader import load_issues
from analytics.bottlenecks import detect_bottlenecks, bottleneck_reason, _is_bottleneck
from analytics.scoring import compute_health_score
from analytics.rag import classify_rag
from models.issue import IssueWithScore
from models.response import make_response

router = APIRouter(prefix="/api/v1", tags=["bottlenecks"])


@router.get("/bottlenecks")
def get_bottlenecks(
    space: str | None = Query(
        None,
        description="Filter by space name, e.g. 'TSA-SITE', 'Voice Policy Engine 2.0', 'RCEM 3.0', 'RCEM 3.2'",
    ),
    fix_version: str | None = Query(
        None,
        description="Filter by exact fix version name, e.g. 'SITE 14.1', 'SITE 14.1 GR', 'VPE2.0.22.6.0'",
    ),
) -> dict:
    issues = load_issues()
    if space:
        issues = [i for i in issues if i.space == space]
    if fix_version:
        issues = [i for i in issues if i.fix_version == fix_version]
    flagged = detect_bottlenecks(issues)
    result = [
        IssueWithScore(
            **i.model_dump(),
            health_score=compute_health_score(i),
            rag=classify_rag(compute_health_score(i)),
            bottleneck=True,
            bottleneck_reason=bottleneck_reason(i),
        )
        for i in flagged
    ]
    return make_response([r.model_dump() for r in result])
