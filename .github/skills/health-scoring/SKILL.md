---
name: health-scoring
description: "Modify health scoring weights, RAG thresholds, or bottleneck detection rules for the Engineering Delivery Health Analyzer. USE FOR: changing RAG color thresholds; adjusting scoring formula weights; adding new bottleneck rules; adding a new status or priority to the scoring tables; explaining why an issue has a specific score. DO NOT USE FOR: JIRA field mappings; frontend chart colors; API route structure."
argument-hint: "Describe the scoring change, e.g. 'make Blocked items score 0 for all weights' or 'add a 4th RAG tier'"
---

# Health Scoring Skill

## Key Files

| File | Purpose |
|---|---|
| `backend/analytics/scoring.py` | `compute_health_score(issue)` → int 0–100 |
| `backend/analytics/rag.py` | `classify_rag(score)` → `"Red"\|"Amber"\|"Green"` |
| `backend/analytics/bottlenecks.py` | `_is_bottleneck(issue)` + `detect_bottlenecks(issues)` |
| `backend/models/issue.py` | `Issue`, `IssueWithScore`, `HealthSummary` Pydantic models |

## Scoring Formula

```
score = round(
    0.4 × status_score +
    0.3 × priority_score +
    0.3 × age_score
)
age_score = max(0, 100 - days_open × decay_rate)
```

The `decay_rate` is **type-aware** — different issue types have different acceptable open windows:

### Age Decay Rates by Type
| Type | Decay rate | Age hits 0 at | Rationale |
|---|---|---|---|
| `Bug` | 7.0 pts/day | ~14 days | QE/testing defects must be fixed within a sprint |
| `Task` | 3.0 pts/day | ~33 days | Should close within one or two sprints |
| `Improvement` | 2.0 pts/day | ~50 days | Medium-term work |
| `Feature` | 1.0 pts/day | ~100 days | Stories can span a full release cycle |

> **Note:** `QE Defect`, `General Testing Defect`, and `External Defect` all map to `Bug` type — they are the fastest-decaying category.

### Status Scores (weight 40%)
| Status | Score |
|---|---|
| `Done` | 100 |
| `In Progress` | 70 |
| `Open` | 50 |
| `Blocked` | 0 |

### Priority Scores (weight 30%)
| Priority | Score |
|---|---|
| `Low` | 100 |
| `Medium` | 75 |
| `High` | 40 |
| `Critical` | 10 |

### Age Score (weight 30%)
`max(0, 100 - days_open × 2)` — hits zero at 50 days open.

## RAG Thresholds

| RAG | Score range | Hex color | Tailwind |
|---|---|---|---|
| Green | ≥ 75 | `#22c55e` | `bg-green-500` |
| Amber | 50–74 | `#f59e0b` | `bg-amber-400` |
| Red | < 50 | `#ef4444` | `bg-red-500` |

**Team score** = average of all non-Done issues. Returns 100 if no active issues.

## Bottleneck Rules (OR logic — any one triggers)

Stale thresholds are **type-aware**:

| Rule | Condition |
|---|---|
| 1 | `status == "Blocked"` (any type) |
| 2 | `priority == "Critical"` AND `days_open > 5` (any type) |
| 3 | `status == "In Progress"` AND `days_open > threshold` (by type) |
| 4 | `status == "Open"` AND `days_open > threshold` (by type) |

**Stale thresholds by type:**

| Type | In Progress stale after | Open stale after |
|---|---|---|
| `Bug` | 7 days | 5 days |
| `Task` | 14 days | 10 days |
| `Improvement` | 14 days | 21 days |
| `Feature` | 21 days | 30 days |

**Sort order:** Blocked issues first, then by `days_open` descending.

## Procedure: Change a Scoring Weight

1. Read `backend/analytics/scoring.py`
2. Adjust the three multipliers — they must sum to 1.0:
   ```python
   score = round(0.4 * status_score + 0.3 * priority_score + 0.3 * age_score)
   #              ^^^                   ^^^                   ^^^
   #           change these, must sum to 1.0
   ```
3. No model or route changes needed — `compute_health_score()` is self-contained

## Procedure: Change RAG Thresholds

1. Read `backend/analytics/rag.py`
2. Edit the if/elif chain — keep thresholds in descending order:
   ```python
   if score >= 75:   return "Green"
   if score >= 50:   return "Amber"
   return "Red"
   ```
3. If adding a new tier (e.g. `"Blue"` ≥ 90), also update:
   - `IssueWithScore.rag` annotation in `models/issue.py` if using a Literal type
   - Frontend RAG color constants in `frontend/src/` (coordinate with dashboard-builder agent)

## Procedure: Add a New Bottleneck Rule

1. Read `backend/analytics/bottlenecks.py`
2. Add a condition to `_is_bottleneck()`:
   ```python
   if issue.priority == "High" and issue.days_open > 30:
       return True, "High priority stale (>30 days)"
   ```
3. The second return value is the `bottleneck_reason` string surfaced in the API
4. Update sort order in `detect_bottlenecks()` if the new rule warrants different ranking

## Procedure: Explain a Specific Issue's Score

Given an issue, calculate manually:
```
decay_rate   = {Bug:7.0, Task:3.0, Improvement:2.0, Feature:1.0}[type]
age_score    = max(0, 100 - days_open × decay_rate)
status_score = {Done:100, In Progress:70, Open:50, Blocked:0}[status]
priority_score = {Low:100, Medium:75, High:40, Critical:10}[priority]
score = round(0.4 × status_score + 0.3 × priority_score + 0.3 × age_score)
```

Example — `TSITE-8094` (Blocked, Medium, Bug, 566 days):
```
decay_rate    = 7.0    (Bug)
age_score     = max(0, 100 - 566×7) = 0
status_score  = 0      (Blocked)
priority_score= 75     (Medium)
score = round(0.4×0 + 0.3×75 + 0.3×0) = round(22.5) = 23  → Red
```

Example — `TSITE-12413` (In Progress, Medium, Bug, 10 days):
```
decay_rate    = 7.0    (Bug)
age_score     = max(0, 100 - 10×7) = 30
status_score  = 70     (In Progress)
priority_score= 75     (Medium)
score = round(0.4×70 + 0.3×75 + 0.3×30) = round(28+22.5+9) = 60  → Amber
```
