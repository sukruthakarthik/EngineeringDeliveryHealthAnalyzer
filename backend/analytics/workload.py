from __future__ import annotations

from collections import Counter

from models.issue import Issue


def workload_distribution(issues: list[Issue]) -> dict[str, int]:
    """Return count of open (non-Done) issues by priority bucket."""
    active = [i for i in issues if i.status != "Done"]
    counts: Counter[str] = Counter(i.priority for i in active)
    order = ["Critical", "High", "Medium", "Low"]
    return {p: counts.get(p, 0) for p in order}
