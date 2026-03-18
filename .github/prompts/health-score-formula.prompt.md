---
description: "Design and implement the health score formula for the Engineering Delivery Health Analyzer. Use this prompt to reason about or update the scoring weights in backend/analytics/scoring.py."
---

# Health Score Formula

Implement the function `compute_health_score(issue: Issue) -> int` in `backend/analytics/scoring.py`.

## Scoring Formula
The score is a weighted composite (0–100) of three factors:

### 1. Status Score (weight: 40%)
| Status | Score |
|--------|-------|
| Done | 100 |
| In Progress | 70 |
| Open | 50 |
| Blocked | 0 |

### 2. Priority Score (weight: 30%)
| Priority | Score |
|----------|-------|
| Low | 100 |
| Medium | 75 |
| High | 40 |
| Critical | 10 |

### 3. Age Score (weight: 30%)
```
age_score = max(0, 100 - days_open * 2)
```
An issue open for 50+ days scores 0. An issue open 1 day scores 98.

### Final Formula
```python
score = round(0.4 * status_score + 0.3 * priority_score + 0.3 * age_score)
return max(0, min(100, score))
```

## Also implement
- `compute_team_score(issues: list[Issue]) -> int` — average of all individual scores (excluding Done items from the risk view)
- Include unit tests as doctest examples in the function docstring

## Output
Write the complete `scoring.py` file. No explanation needed.
