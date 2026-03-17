from __future__ import annotations

from models.issue import Issue


_STATUS_SCORES: dict[str, int] = {
    "Done": 100,
    "In Progress": 70,
    "Open": 50,
    "Blocked": 0,
}

_PRIORITY_SCORES: dict[str, int] = {
    "Low": 100,
    "Medium": 75,
    "High": 40,
    "Critical": 10,
}

# Age decay rates by issue type (points lost per day open).
# age_score = max(0, 100 - days_open * rate)
# Rationale:
#   Bug            — QE/General/External defects must be fixed fast (~14 days)
#   Task           — Should close within a sprint (~33 days)
#   Improvement    — Medium-term work (~50 days)
#   Feature/Story  — Can span a release cycle (~100 days)
_AGE_DECAY_RATE: dict[str, float] = {
    "Bug": 7.0,
    "Task": 3.0,
    "Improvement": 2.0,
    "Feature": 1.0,
}


def compute_health_score(issue: Issue) -> int:
    """Return a 0–100 health score for a single issue.

    Age decay rate is type-aware: Bugs decay fastest (~14 days to 0),
    Features slowest (~100 days to 0).

    >>> from models.issue import Issue
    >>> done = Issue(issue_id="J-1", title="t", status="Done", priority="Low", days_open=1, assignee="a", fix_version="s", type="Task")
    >>> compute_health_score(done)
    100
    >>> blocked = Issue(issue_id="J-2", title="t", status="Blocked", priority="Critical", days_open=20, assignee="a", fix_version="s", type="Bug")
    >>> compute_health_score(blocked)
    0
    """
    status_score = _STATUS_SCORES.get(issue.status, 50)
    priority_score = _PRIORITY_SCORES.get(issue.priority, 50)
    decay_rate = _AGE_DECAY_RATE.get(issue.type, 2.0)
    age_score = max(0, 100 - issue.days_open * decay_rate)
    raw = 0.4 * status_score + 0.3 * priority_score + 0.3 * age_score
    return max(0, min(100, round(raw)))


def compute_team_score(issues: list[Issue]) -> int:
    """Return the average health score across all non-Done issues.

    Falls back to 100 when there are no active issues.
    """
    active = [i for i in issues if i.status != "Done"]
    if not active:
        return 100
    return round(sum(compute_health_score(i) for i in active) / len(active))
