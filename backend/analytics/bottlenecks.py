from __future__ import annotations

from models.issue import Issue


# Stale thresholds by issue type (days before flagging as bottleneck).
# Bugs in a testing cycle should be resolved much faster than Stories.
_STALE_IN_PROGRESS: dict[str, int] = {
    "Bug": 7,          # QE/General defects stale after 1 week in progress
    "Task": 14,        # Tasks stale after 2 weeks
    "Improvement": 14,
    "Feature": 21,     # Stories can legitimately span sprints
}

_STALE_OPEN: dict[str, int] = {
    "Bug": 5,          # Unstarted bugs are urgent after 5 days
    "Task": 10,
    "Improvement": 21,
    "Feature": 30,     # Stories sit in backlog longer
}


def _is_bottleneck(issue: Issue) -> bool:
    if issue.status == "Blocked":
        return True
    if issue.priority == "Critical" and issue.days_open > 5:
        return True
    stale_ip = _STALE_IN_PROGRESS.get(issue.type, 14)
    if issue.status == "In Progress" and issue.days_open > stale_ip:
        return True
    stale_open = _STALE_OPEN.get(issue.type, 21)
    if issue.status == "Open" and issue.days_open > stale_open:
        return True
    return False


def bottleneck_reason(issue: Issue) -> str:
    if issue.status == "Blocked":
        return "Blocked status"
    if issue.priority == "Critical" and issue.days_open > 5:
        return f"Critical priority open for {issue.days_open} days"
    stale_ip = _STALE_IN_PROGRESS.get(issue.type, 14)
    if issue.status == "In Progress" and issue.days_open > stale_ip:
        return f"{issue.type} in progress for {issue.days_open} days (stale after {stale_ip}d)"
    stale_open = _STALE_OPEN.get(issue.type, 21)
    if issue.status == "Open" and issue.days_open > stale_open:
        return f"{issue.type} open for {issue.days_open} days (overdue after {stale_open}d)"
    return ""


def detect_bottlenecks(issues: list[Issue]) -> list[Issue]:
    """Return issues that are bottlenecks, sorted by severity.

    Sort order: Blocked items first, then by days_open descending.
    """
    flagged = [i for i in issues if _is_bottleneck(i)]
    return sorted(flagged, key=lambda i: (i.status != "Blocked", -i.days_open))
