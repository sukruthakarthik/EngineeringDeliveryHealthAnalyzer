from fastapi import APIRouter, Query

from analytics.data_loader import load_issues
from analytics.scoring import compute_health_score, compute_team_score
from analytics.rag import classify_rag
from analytics.bottlenecks import _is_bottleneck, bottleneck_reason
from models.issue import IssueWithScore, HealthSummary, ReleaseHealth, SpaceHealthSummary
from models.response import make_response

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health-score")
def get_health_score(
    project: str | None = Query(
        None,
        description="Filter by JIRA project ID, e.g. 'TSITE', 'VPE2', 'RCEM3', 'RCEM32'",
    ),
    fix_version: str | None = Query(
        None,
        description="Filter by exact fix version name, e.g. 'SITE 14.1', 'SITE 14.1 GR', 'VPE2.0.22.6.0'",
    ),
) -> dict:
    issues = load_issues()
    if project:
        issues = [i for i in issues if i.project == project]
    if fix_version:
        issues = [i for i in issues if i.fix_version == fix_version]
    team_score = compute_team_score(issues)
    issues_with_scores: list[IssueWithScore] = []
    for issue in issues:
        score = compute_health_score(issue)
        is_bn = _is_bottleneck(issue)
        issues_with_scores.append(
            IssueWithScore(
                **issue.model_dump(),
                health_score=score,
                rag=classify_rag(score),
                bottleneck=is_bn,
                bottleneck_reason=bottleneck_reason(issue) if is_bn else None,
            )
        )
    summary = HealthSummary(
        team_score=team_score,
        rag=classify_rag(team_score),
        total_issues=len(issues),
        issues=issues_with_scores,
    )
    return make_response(summary.model_dump())


@router.get("/health-score/by-release")
def get_health_score_by_release(
    project: str | None = Query(None, description="Filter by JIRA project ID, e.g. 'TSITE', 'VPE2', 'RCEM3', 'RCEM32'. Omit for all projects."),
    limit: int = Query(5, ge=1, le=50, description="Number of most recent fix versions to return (default 5)"),
) -> dict:
    """Return health score aggregated per fix version.

    Returns the `limit` most recent fix versions (by release date, falling back
    to version name when date is absent), both released and in-progress.
    Each entry includes a `released` flag so the frontend can distinguish them.
    Sorted by date descending (most recent first).
    """
    issues = load_issues()

    # Optionally filter to a single project
    if project:
        issues = [i for i in issues if i.project == project]

    # Group by (space, fix_version) so same-named versions in different spaces stay separate
    groups: dict[tuple[str, str], list] = {}
    for issue in issues:
        groups.setdefault((issue.space, issue.fix_version), []).append(issue)

    results: list[ReleaseHealth] = []
    for (_, fix_version), group_issues in groups.items():
        released = group_issues[0].fix_version_released
        # Use the release date from the first issue in the group (same version = same date)
        fix_version_date = group_issues[0].fix_version_date
        active = [i for i in group_issues if i.status != "Done"]
        release_score = (
            round(sum(compute_health_score(i) for i in active) / len(active))
            if active else 100
        )
        bn_count = sum(1 for i in group_issues if _is_bottleneck(i))
        results.append(ReleaseHealth(
            fix_version=fix_version,
            fix_version_date=fix_version_date,
            released=released,
            space=group_issues[0].space,
            score=release_score,
            rag=classify_rag(release_score),
            total_issues=len(group_issues),
            open_issues=sum(1 for i in group_issues if i.status == "Open"),
            in_progress_issues=sum(1 for i in group_issues if i.status == "In Progress"),
            blocked_issues=sum(1 for i in group_issues if i.status == "Blocked"),
            done_issues=sum(1 for i in group_issues if i.status == "Done"),
            bottleneck_count=bn_count,
        ))

    # Sort by fix_version_date descending; fall back to version name descending when date is absent
    results.sort(key=lambda r: (r.fix_version_date or r.fix_version), reverse=True)
    results = results[:limit]

    return make_response([r.model_dump() for r in results])


@router.get("/health-score/summary")
def get_health_score_summary(
    project: str | None = Query(None, description="Filter by JIRA project ID, e.g. 'TSITE', 'VPE2', 'RCEM3'"),
    fix_version: str | None = Query(None, description="Filter by exact fix version name"),
) -> dict:
    """Lightweight summary: RAG counts + team score, without the full issue list.

    Designed for the landing page cards where individual issues are not needed.
    """
    issues = load_issues()
    if project:
        issues = [i for i in issues if i.project == project]
    if fix_version:
        issues = [i for i in issues if i.fix_version == fix_version]

    red = amber = green = 0
    for issue in issues:
        score = compute_health_score(issue)
        rag = classify_rag(score)
        if rag == "Red":
            red += 1
        elif rag == "Amber":
            amber += 1
        else:
            green += 1

    team_score = compute_team_score(issues)
    space = issues[0].space if issues else ""

    summary = SpaceHealthSummary(
        space=space,
        team_score=team_score,
        rag=classify_rag(team_score),
        total_issues=len(issues),
        red=red,
        amber=amber,
        green=green,
    )
    return make_response(summary.model_dump())
