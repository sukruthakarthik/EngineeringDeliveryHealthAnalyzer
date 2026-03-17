from __future__ import annotations

from pydantic import BaseModel


class Issue(BaseModel):
    issue_id: str
    title: str
    project: str = "SITE"
    status: str
    priority: str
    days_open: int
    assignee: str
    fix_version: str
    fix_version_released: bool = False
    fix_version_date: str = ""   # ISO date string from JIRA, e.g. "2025-11-14"; empty if unset
    space: str = ""  # Confluence space, e.g. "TSA-SITE", "Voice Policy Engine 2.0"
    type: str


class IssueWithScore(Issue):
    health_score: int
    rag: str
    bottleneck: bool
    bottleneck_reason: str | None = None


class HealthSummary(BaseModel):
    team_score: int
    rag: str
    total_issues: int
    issues: list[IssueWithScore]


class ReleaseHealth(BaseModel):
    fix_version: str
    fix_version_date: str  # ISO date from JIRA, e.g. "2025-11-14"; empty if unset
    released: bool
    space: str
    score: int
    rag: str
    total_issues: int
    open_issues: int
    in_progress_issues: int
    blocked_issues: int
    done_issues: int
    bottleneck_count: int
