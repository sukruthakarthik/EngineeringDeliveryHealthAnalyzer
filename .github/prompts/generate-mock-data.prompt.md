---
description: "Generate a realistic mock JIRA-like issues dataset as a JSON file for the Engineering Delivery Health Analyzer. Use this prompt to create or regenerate data/issues.json."
---

# Generate Mock Data

Generate a JSON file at `data/issues.json` containing **50 mock engineering work items** for a software team.

## Schema (each item)
```json
{
  "issue_id": "JIRA-101",
  "title": "Short description of the task",
  "status": "Open | In Progress | Blocked | Done",
  "priority": "Low | Medium | High | Critical",
  "days_open": 7,
  "assignee": "team member name",
  "fix_version": "SITE 15.0",
  "type": "Bug | Feature | Task | Improvement"
}
```

## Distribution Requirements
- **Status**: ~30% Open, ~35% In Progress, ~15% Blocked, ~20% Done
- **Priority**: ~20% Low, ~35% Medium, ~30% High, ~15% Critical
- **Days open**: range 1–45; Blocked items tend to have days_open > 8
- **Assignees**: 5 fictional names, distributed across items (no real PII)
- **Fix Versions**: Spread across `SITE 15.0`, `INTERNAL`, `Unassigned`
- **Types**: mix of Bug, Feature, Task, Improvement

## Output
Write the full JSON array to `data/issues.json`. No extra explanation needed — just the file content.
