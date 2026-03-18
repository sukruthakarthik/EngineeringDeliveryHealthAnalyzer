---
description: "Implement or update the bottleneck detection logic in backend/analytics/bottlenecks.py for the Engineering Delivery Health Analyzer."
---

# Bottleneck Detection

Implement `detect_bottlenecks(issues: list[Issue]) -> list[Issue]` in `backend/analytics/bottlenecks.py`.

## Bottleneck Rules (OR logic — any rule triggers a bottleneck)
1. `status == "Blocked"` — always a bottleneck
2. `priority == "Critical"` AND `days_open > 5`
3. `status == "In Progress"` AND `days_open > 14`
4. `status == "Open"` AND `days_open > 21`

## Also implement
```python
def bottleneck_reason(issue: Issue) -> str:
    """Return a human-readable reason why this issue is a bottleneck."""
```

Example reasons:
- `"Blocked status"`
- `"Critical priority open for 8 days"`
- `"In progress for 18 days (stale)"`
- `"Open for 25 days (overdue)"`

## Sorting
Return bottlenecks sorted by severity:
1. Blocked items first
2. Then by days_open descending

## Output
Write the complete `bottlenecks.py` file. No explanation needed.
